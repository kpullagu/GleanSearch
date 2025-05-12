import boto3
import json
import os
import requests
import re
import uuid
import time
import random  # Import the random module
from urllib.parse import unquote_plus
from datetime import datetime

# --- Configuration from Environment Variables ---
GLEAN_API_TOKEN = os.environ.get("GLEAN_API_TOKEN", "gleantoken")
GLEAN_DATASOURCE = os.environ.get("GLEAN_DATASOURCE", "gleandatasource")
GLEAN_API_ENDPOINT = os.environ.get("GLEAN_API_ENDPOINT", "https://glean-be.glean.com/api/index/v1/indexdocuments")
VIEW_URL_BASE = os.environ.get("VIEW_URL_BASE", "https://en.wikipedia.org/wiki/")


BUCKET_NAME = os.environ.get("BUCKET_NAME")
UPLOAD_ID_PREFIX = "PK"

s3_client = boto3.client('s3')

# Initialize the counter with a random number between 1 and 10,000
counter = random.randint(1, 10000)

def create_document(unique_id, filename, content, metadata):
    """Create document payload for Glean API."""
    global counter  # Use the global counter variable
    view_url = f"{VIEW_URL_BASE}{counter}"  # Generate the view URL using the counter
    counter += 1  # Increment the counter for the next file
    
    return {
        "id": unique_id,  # Use the unique ID
        "title": metadata['title'],
        "datasource": GLEAN_DATASOURCE,
        "objectType": "deal",  # Object type for deals
        "body": {
            "mimeType": "text/plain",
            "textContent": metadata['body']
        },
        "summary": {
            "mimeType": "text/plain",
            "textContent": metadata['summary']
        },
        "viewURL": view_url,
        "permissions": {
            "allowAnonymousAccess": True
        },
        "author": {
            "email": "alex@glean-sandbox.com",
            "name": "KPull"
        },
        "updatedBy": {
            "email": "alex@glean-sandbox.com",
            "name": "KPull"
        },
        "owner": {
            "email": "alex@glean-sandbox.com",
            "name": "KP"
        },
        "status": "active",
        "tags": metadata['tags'],
        "customProperties": metadata['customProperties']
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
    #print(json.dumps(payload, indent=4))  # Pretty-print the payload for debugging
    #print(f"Payload being sent:\n{json.dumps(payload, indent=4)}")
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
            
            #if not key.startswith('deals/'):  # Updated to check for 'deals/' folder
            if not key.startswith('new/'):  # Updated to check for 'deals/' folder

                continue
                
            try:
                content = get_file_content(bucket, key)
                filename = os.path.basename(key)
                # Parse metadata from the deal object file
                metadata = parse_deal_file(content)                
                doc_id = metadata['doc_id']
                unique_id = f"{doc_id}_{os.path.splitext(filename)[0]}"
                doc = create_document(unique_id, filename, content, metadata)
                documents.append(doc)
                files_to_move.append({'bucket': bucket, 'old_key': key, 'title': metadata['title']})
                print(f"Successfully processed file: {key}")
                
            except Exception as e:
                print(f"Error processing file {key}: {str(e)}")
                continue
    
    if documents:
        if call_glean_bulk_api(documents):
            move_processed_files(files_to_move)
        else:
            print("Failed to index documents in Glean. Files will remain in 'deals' folder.")
    
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
    metadata['body'] = extract_field(content, "Body", is_multiline=True)  # Extract full body
    metadata['summary'] = extract_field(content, "Executive Summary", is_multiline=False)  # Extract single-line summary
    
    # Extract CustomProperties as JSON
    custom_props = extract_field(content, "CustomProperties", is_json=True)
    if custom_props:
        metadata['customProperties'] = [
            {"name": key, "value": value} for key, value in custom_props.items()
        ]
    else:
        metadata['customProperties'] = [{"name": "author", "value": "KPull"}]  # Default value if not found
    
    return metadata

def parse_deal_file(content):
    """Parse deal object file and extract relevant fields."""
    try:
        deal_data = json.loads(content)
        doc_id = deal_data.get("objectId", "unknown_id")
        title = deal_data["properties"].get("dealname", "Untitled Deal")
        body = f"Deal Amount: {deal_data['properties'].get('amount', 'N/A')}\n" \
               f"Deal Stage: {deal_data['properties'].get('dealstage', 'N/A')}"
        summary = f"Pipeline: {deal_data['properties'].get('pipeline', 'N/A')}"
        tags = ["deal"]  # Default tag for deals
        custom_properties = [
            {"name": "hubspot_owner_id", "value": deal_data["properties"].get("hubspot_owner_id", "N/A")},
            {"name": "createdate", "value": deal_data["properties"].get("createdate", "N/A")},
            {"name": "hs_lastmodifieddate", "value": deal_data["properties"].get("hs_lastmodifieddate", "N/A")}
        ]
        return {
            "doc_id": doc_id,
            "title": title,
            "body": body,
            "summary": summary,
            "tags": tags,
            "customProperties": custom_properties
        }
    except Exception as e:
        print(f"Error parsing deal file: {e}")
        raise

def extract_field(content, field_name, is_list=False, is_json=False, is_multiline=False):
    """Extract a specific field from the content."""
    import re
    # Use re.DOTALL if is_multiline is True to match across multiple lines
    match = re.search(rf"{field_name}:(.*)", content, re.DOTALL if is_multiline else 0)
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
    return [] if is_list else {} if is_json else ""

def move_processed_files(files):
    """Move processed files to 'processed' folder"""
    for file in files:
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            # Extract the filename without extension from the old_key
            filename_without_extension = os.path.splitext(os.path.basename(file['old_key']))[0]
            new_key = f"processed/{timestamp}_{filename_without_extension}.txt"            
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
