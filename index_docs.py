#!/usr/bin/env python3
import requests
import os
import json
import re

# Configuration
GLEAN_API_ENDPOINT = "https://glean-be-be.glean.com/api/index/v1/indexdocuments" # Bulk endpoint
API_TOKEN = "gleantoken=" # Glean Token
DATASOURCE_NAME = "gleandatasource" # Datasource name
SAMPLE_DOCS_DIR = "sample_docs" # Local directory containing sample documents

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

def index_document(doc_id, title, body, filename):
    """Indexes a single document using the Glean API."""
    payload = {
        "document": {
            "id": doc_id,
            "title": title,
            "datasource": DATASOURCE_NAME,
            "objectType": "sampleTextDoc", # A simple object type for these samples
            "body": {
                "mimeType": "text/plain",
                "textContent": body
            },
            "permissions": {
                "allowAnonymousAccess": True # Allow anonymous access for this example
                
                },
            # Providing a viewURL is good practice, even if it's a local file
            # path for this example
            "viewURL": f"https://ncbi.nlm.nih.gov/pubmed/{filename}.txt" 
        }
    }
    
    try:
        response = requests.post(GLEAN_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        print(f"Successfully indexed {filename} (ID: {doc_id}). Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error indexing {filename} (ID: {doc_id}): {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"Response content: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response content: {e.response.text}")
        return False

def main():
    """Iterates through sample documents and indexes them."""
    print(f"Starting indexing process for datasource '{DATASOURCE_NAME}'...")
    indexed_count = 0
    error_count = 0
    
    for filename in sorted(os.listdir(SAMPLE_DOCS_DIR)):
        if filename.endswith(".txt"):
            file_path = os.path.join(SAMPLE_DOCS_DIR, filename)
            doc_id = os.path.splitext(filename)[0] # Use filename without extension as ID
            
            title, body = parse_document(file_path)
            
            if title is not None and body is not None:
                if index_document(doc_id, title, body, filename):
                    indexed_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
                
    print(f"\nIndexing process finished.")
    print(f"Successfully indexed: {indexed_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    main()

