#!/usr/bin/env python3
import json
import os
import urllib.parse
import boto3
import magic
import requests
import uuid
import re
import time

# --- Configuration (Use Environment Variables in Lambda) ---
GLEAN_API_TOKEN = os.environ.get("GLEAN_API_TOKEN", "glean_token")
GLEAN_DATASOURCE = os.environ.get("GLEAN_DATASOURCE", "gleandatasource")
GLEAN_API_ENDPOINT = os.environ.get("GLEAN_API_ENDPOINT", "https://glean-be.glean.com/api/index/v1/bulkindexdocuments")
UPLOAD_ID_PREFIX = "PK"
VIEW_URL_BASE = "https://en.wikipedia.org/wiki/"
OBJECT_TYPE = "sampleTextDoc"  # Update to match your Glean schema

# --- AWS Client ---
s3 = boto3.client("s3")

# --- Functions ---

def get_file_content_from_s3(bucket, key):
    local_path = f"/tmp/{os.path.basename(key)}"
    try:
        print(f"Downloading s3://{bucket}/{key} to {local_path}")
        s3.download_file(bucket, key, local_path)

        mime_type = magic.from_file(local_path, mime=True)
        print(f"Detected MIME type: {mime_type}")

        if not mime_type.startswith("text/"):
            print(f"Skipping non-text file: {mime_type}")
            return None, None

        with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content, mime_type
    except Exception as e:
        print(f"Error reading from S3: {e}")
        return None, None
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

def create_document(doc_id, title, content, mime_type):
    view_url = f"{VIEW_URL_BASE}{title}"
    return {
        "id": doc_id,
        "datasource": GLEAN_DATASOURCE,
        "objectType": OBJECT_TYPE,
        "title": title,
        "viewURL": view_url,
        "permissions": {
            "allowAllDatasourceUsersAccess": True
        },
        "customProperties": [
            {
                "name": "Org",
                "value": "Infrastructure"
            }
        ],
        "body": {
            "mimeType": mime_type or "text/plain",
            "textContent": content
        }
    }

def call_glean_bulk_api(document):
    upload_id = f"upload_{uuid.uuid4().hex}_{int(time.time())}"
    payload = {
        "uploadId": upload_id,
        "isFirstPage": True,
        "isLastPage": True,
        "forceRestartUpload": True,
        "datasource": GLEAN_DATASOURCE,
        "documents": [document]
    }

    headers = {
        "Authorization": f"Bearer {GLEAN_API_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"Uploading document with uploadId: {upload_id}")
    try:
        response = requests.post(GLEAN_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        print("Upload successful.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error uploading to Glean: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                print("Response:", e.response.json())
            except json.JSONDecodeError:
                print("Response text:", e.response.text)
        return False

# --- Lambda Handler ---

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    processed = 0
    failed = 0

    for record in event.get("Records", []):
        if record.get("eventSource") != "aws:s3":
            continue

        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        print(f"Processing S3 object: s3://{bucket}/{key}")
        content, mime_type = get_file_content_from_s3(bucket, key)
        if not content:
            failed += 1
            continue

        doc = create_document(doc_id=key, title=os.path.basename(key), content=content, mime_type=mime_type)
        if call_glean_bulk_api(doc):
            processed += 1
        else:
            failed += 1

    print(f"Processed: {processed}, Failed: {failed}")
    return {
        "statusCode": 200 if failed == 0 else 500,
        "body": f"Processed: {processed}, Failed: {failed}"
    }
