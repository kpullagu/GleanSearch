import boto3
import json
import os
import requests
import uuid
import time
import random  # Import the random module
from urllib.parse import unquote_plus
from datetime import datetime

# --- Configuration from Environment Variables ---
GLEAN_API_TOKEN = os.environ.get("GLEAN_API_TOKEN", "gleantoken")
GLEAN_DATASOURCE = os.environ.get("GLEAN_DATASOURCE", "gleandatasource")
GLEAN_API_ENDPOINT = os.environ.get("GLEAN_API_ENDPOINT", "https://glean-be.glean.com/api/index/v1/bulkindexdocuments")
VIEW_URL_BASE = os.environ.get("VIEW_URL_BASE", "https://ncbi.nlm.nih.gov/pubmed/")
OBJECT_TYPE = os.environ.get("OBJECT_TYPE", "sampleTextDoc")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
UPLOAD_ID_PREFIX = "PK"

s3_client = boto3.client('s3')

# Initialize the counter with a random number between 1 and 10,000
counter = random.randint(1, 10000)

def create_document(doc_id, title, content, filename, metadata):
    """Create document payload for Glean API"""
    global counter  # Use the global counter variable
    view_url = f"{VIEW_URL_BASE}{counter}"  # Generate the view URL using the counter
    counter += 1  # Increment the counter for the next file
    
    mime_type = "text/plain"  # Hardcoded since we only deal with plain text files
    
    return {
        "id": doc_id,
        "datasource": GLEAN_DATASOURCE,
        "objectType": metadata.get("objectType", OBJECT_TYPE),
        "title": title,
        "viewURL": view_url,
        "permissions": {
            "allowAllDatasourceUsersAccess": True
        },
        "customProperties": [
            {"name": key, "value": value} for key, value in metadata.get("customProperties", {}).items()
        ],
        "tags": metadata.get("tags", ["default-tag"]),
        "body": {
            "mimeType": mime_type,
            "textContent": content
        }
    }

def call_glean_bulk_api(documents):
    """Call Glean bulk API with the provided documents"""
    upload_id = f"upload_{uuid.uuid4().hex}_{int(time.time())}"
    payload = {
        "uploadId": upload_id,
        "isFirstPage": True,
        "isLastPage": True,
        "forceRestartUpload": True,
        "datasource": GLEAN_DATASOURCE,
        "documents": documents
    }

    headers = {
        "Authorization": f"Bearer {GLEAN_API_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"Uploading batch with uploadId: {upload_id}")
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

def lambda_handler(event, context):
    print(f"Processing batch of {len(event['Records'])} messages")
    
    documents = []
    files_to_move = []
    
    for record in event['Records']:
        body = json.loads(record['body'])
        s3_event = json.loads(body['Message']) if 'Message' in body else body
        
        for s3_record in s3_event['Records']:
            bucket = s3_record['s3']['bucket']['name']
            key = unquote_plus(s3_record['s3']['object']['key'])
            
            if not key.startswith('new/'):
                continue
                
            try:
                content = get_file_content(bucket, key)
                filename = os.path.basename(key)
                title = os.path.splitext(filename)[0]
                doc_id = f"{UPLOAD_ID_PREFIX}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{title}"
                
                # Parse metadata from the file content
                metadata = parse_metadata(content)
                
                doc = create_document(doc_id, title, content, filename, metadata)
                documents.append(doc)
                files_to_move.append({'bucket': bucket, 'old_key': key, 'title': title})
                print(f"Successfully processed file: {key}")
                
            except Exception as e:
                print(f"Error processing file {key}: {str(e)}")
                continue
    
    if documents:
        if call_glean_bulk_api(documents):
            move_processed_files(files_to_move)
        else:
            print("Failed to index documents in Glean. Files will remain in 'new' folder.")
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed and moved {len(documents)} documents')
    }

def get_file_content(bucket, key):
    """Get file content from S3"""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body'].read().decode('utf-8')

def parse_metadata(content):
    """Parse metadata from the file content"""
    metadata = {}
    metadata['title'] = extract_field(content, "Title")
    metadata['objectType'] = extract_field(content, "ObjectType")
    metadata['tags'] = extract_field(content, "Tags", is_list=True)
    custom_props = extract_field(content, "CustomProperties", is_json=True)
    metadata['customProperties'] = custom_props if custom_props else {}
    return metadata

def extract_field(content, field_name, is_list=False, is_json=False):
    """Extract a specific field from the content"""
    import re
    match = re.search(rf"{field_name}: (.*)", content)
    if match:
        value = match.group(1).strip()
        if is_list:
            return value.split(", ")
        if is_json:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        return value
    return [] if is_list else {} if is_json else None

def move_processed_files(files):
    """Move processed files to 'processed' folder"""
    for file in files:
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            new_key = f"processed/{timestamp}_{file['title']}.txt"
            
            s3_client.copy_object(
                Bucket=file['bucket'],
                CopySource={'Bucket': file['bucket'], 'Key': file['old_key']},
                Key=new_key
            )
            
            s3_client.delete_object(
                Bucket=file['bucket'],
                Key=file['old_key']
            )
            
            print(f"Moved file from {file['old_key']} to {new_key}")
            
        except Exception as e:
            print(f"Error moving file {file['old_key']}: {str(e)}")
