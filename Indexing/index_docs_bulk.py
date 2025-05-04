#!/usr/bin/env python3
import requests
import os
import json
import re
import uuid
import random
import time

# Configuration
GLEAN_API_ENDPOINT = "https://glean-be.glean.com/api/index/v1/indexdocuments" # Bulk endpoint
API_TOKEN = "my_index_token" # Glean Token
DATASOURCE_NAME = "MY_DATA_SOURCE_NAME" # Datasource name
SAMPLE_DOCS_DIR = "sample_docs" # Local directory containing sample documents
# Define a base URL that matches the expected pattern
VIEW_URL_BASE = "https://ncbi.nlm.nih.gov/pubmed/" # Base URL for viewURL

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def parse_document(file_path):
    """Parses document with structured metadata."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Parse structured metadata with error handling
    metadata = {}
    metadata['title'] = re.search(r"Title: (.*)", content)
    metadata['objectType'] = re.search(r"ObjectType: (.*)", content)
    metadata['tags'] = re.search(r"Tags: (.*)", content)
    custom_props_match = re.search(r"CustomProperties: ({.*})", content, re.DOTALL)
    body_match = re.search(r"Body:\n(.*)", content, re.DOTALL)
    
    # Extract values or set defaults
    metadata['title'] = metadata['title'].group(1) if metadata['title'] else "Untitled"
    metadata['objectType'] = metadata['objectType'].group(1) if metadata['objectType'] else "sampleTextDoc"
    metadata['tags'] = metadata['tags'].group(1).split(', ') if metadata['tags'] else ["KP-Docs"]
    
    # Ensure customProperties is an array of objects
    if custom_props_match:
        custom_properties_dict = json.loads(custom_props_match.group(1))
        metadata['customProperties'] = [
            {"name": key, "value": value} for key, value in custom_properties_dict.items()
        ]
    else:
        metadata['customProperties'] = [{"name": "author", "value": "KPull"}]
    
    body = body_match.group(1).strip() if body_match else ""
    
    if not metadata['objectType']:
        raise ValueError(f"Missing 'ObjectType' in document: {file_path}")
    
    return metadata, body


def prepare_documents_payload():
    """Prepares the list of document objects for the bulk API payload."""
    documents_list = []
    print(f"Preparing documents from {SAMPLE_DOCS_DIR}...")
    increment_number = random.randint(1, 10000)  # Start with random increment number
    # Iterate through all files in the sample documents directory    
    for filename in sorted(os.listdir(SAMPLE_DOCS_DIR)):
        if filename.endswith(".txt"):
            file_path = os.path.join(SAMPLE_DOCS_DIR, filename)
            metadata, body = parse_document(file_path)
            
            document_object = {
                "id": os.path.splitext(filename)[0],
                "title": metadata['title'],
                "datasource": DATASOURCE_NAME,
                "objectType": metadata['objectType'],
                "body": {
                    "mimeType": "text/plain",
                    "textContent": body
                },
                "viewURL": f"{VIEW_URL_BASE}{increment_number}",
                "permissions": {
                    "allowAnonymousAccess": True
                },
                "tags": metadata['tags'],
                "customProperties": metadata['customProperties']
            }
            documents_list.append(document_object)
            increment_number += 1  # Increment the number for the next document
    print(f"Prepared {len(documents_list)} documents for indexing.")
    
    return documents_list




def index_documents_bulk(documents_list):
    """Indexes a batch of documents using the Glean /indexdocuments API."""
    if not documents_list:
        print("No documents to index.")
        return False
        
    # Generate a unique upload ID for this batch
    upload_id = "KP-Test"
    
    payload = {
        "uploadId": upload_id,
        "datasource": DATASOURCE_NAME,
        "documents": documents_list
    }
    
    print(f"Sending bulk indexing request (Upload ID: {upload_id}) with {len(documents_list)} documents...")
    print(json.dumps(payload, indent=4))  # Pretty-print the payload for debugging
    print(f"Payload being sent:\n{json.dumps(payload, indent=4)}")
    
    try:
        response = requests.post(GLEAN_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        print(f"Successfully submitted bulk indexing request. Status: {response.status_code}")
        print(f"Response: {response.text}") # Print response body if any
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error submitting bulk indexing request (Upload ID: {upload_id}): {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response content: {e.response.text}")
        return False

def main():
    """Prepares documents and sends them to the bulk indexing API."""
    print(f"Starting bulk indexing process for datasource '{DATASOURCE_NAME}'...")
    documents_to_index = prepare_documents_payload()
    
    if documents_to_index:
        success = index_documents_bulk(documents_to_index)
        if success:
            print("\nBulk indexing request submitted successfully.")
        else:
            print("\nBulk indexing request failed.")
    else:
        print("\nNo documents were prepared for indexing.")

if __name__ == "__main__":
    main()

