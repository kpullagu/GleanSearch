#!/usr/bin/env python3
import requests
import os
import json
import re
import uuid

# Configuration
GLEAN_API_ENDPOINT = "https://support-lab-be.glean.com/api/index/v1/indexdocuments" # Bulk endpoint
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
    """Parses title and body from a sample document file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        title_match = re.search(r"^Title: (.*)", content, re.MULTILINE)
        body_match = re.search(r"^Body:\n(.*)", content, re.MULTILINE | re.DOTALL)
        
        title = title_match.group(1).strip() if title_match else "Untitled Document"
        body = body_match.group(1).strip() if body_match else ""
        
        return title, body
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return None, None

def prepare_documents_payload():
    """Prepares the list of document objects for the bulk API payload."""
    documents_list = []
    print(f"Preparing documents from {SAMPLE_DOCS_DIR}...")
    increment_number = 1000100  # Start increment number from 1000100
    # Iterate through all files in the sample documents directory    
    for filename in sorted(os.listdir(SAMPLE_DOCS_DIR)):
        if filename.endswith(".txt"):
            file_path = os.path.join(SAMPLE_DOCS_DIR, filename)
            doc_id = os.path.splitext(filename)[0] # Use filename without extension as ID
            
            title, body = parse_document(file_path)
            
            if title is not None and body is not None:
                # Generate viewURL matching the expected pattern
                view_url = f"{VIEW_URL_BASE}{increment_number}"
                increment_number += 1  # Increment the number for the next file
                
                document_object = {
                    "id": doc_id,
                    "title": title,
                    "datasource": DATASOURCE_NAME, 
                    "objectType": "sampleTextDoc", 
                    "body": {
                        "mimeType": "text/plain",
                        "textContent": body
                    },
                    "viewURL": view_url, # Use the generated URL
                    "permissions": { # Added permissions based on API error
                        "allowAnonymousAccess": True 
                    },
                    "tags": ["Name", "KP-Test"],
                }
                documents_list.append(document_object)
            else:
                print(f"Skipping file due to parsing error: {filename}")
                
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

