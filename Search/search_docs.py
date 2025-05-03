#!/usr/bin/env python3
import requests
import json
import argparse

# Configuration
GLEAN_SEARCH_API_ENDPOINT = "https://support-lab-be.glean.com/rest/api/v1/search"  # Assumed search endpoint
API_TOKEN = "my_dummy_token"  # Token provided by user

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def search_glean(query):
    """Performs a search query using the Glean Search API."""
    payload = {
        "query": query,
        "datasourcesFilter": ["interviewds"],  # Filter by our specific datasource
        "pageSize": 4,  # Optional: Limit the number of results per page
        "includeFields": ["datasource", "metadata", "title", "url", "document"],
        "pageToken": None  # Optional: For pagination, set the token for the next page
    }
    
    print(f"Sending search request for query: '{query}'...")
    
    try:
        response = requests.post(GLEAN_SEARCH_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        #print(f"Search request successful. response: {response.json()}")

        print(f"Search request successful. Status: {response.status_code}")
        search_results = response.json()
        
        print("\nSearch Results:")
        if search_results.get("results"):
            for i, result in enumerate(search_results["results"]):
                print(f"  Result {i+1}:")
                # Adjust field names based on actual API response if needed
                doc = result.get("document", {})
                print(f"    Document ID: {doc.get("id", "N/A")}")
                print(f"    Title: {doc.get('title', 'N/A')}")
                print(f"    URL: {doc.get('url', 'N/A')}")
                #print(f"    Body: {doc.get('bodySnippet', 'N/A')}")
                # Extract the first snippet text
                snippets = new_func(result)
                first_snippet_text = snippets[0].get("text", "No snippet available.") if snippets else "No snippet available."
                print(f"    Body: {first_snippet_text}")  # Use the first snippet text as the body
                print("---")
            print(f"Total results: {len(search_results['results'])}")
        else:
            print("No results found.")
            # Print full response if no results found, for debugging
            print(json.dumps(search_results, indent=2))
            
        return search_results
        
    except requests.exceptions.RequestException as e:
        print(f"Error submitting search request: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response content: {e.response.text}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response from search API.")
        print(f"Response text: {response.text}")
        return None

def new_func(result):
    snippets = result.get("snippets", [])
    return snippets

def main():
    """Parses arguments and calls the search function."""
    parser = argparse.ArgumentParser(description="Search Glean index.")
    parser.add_argument("query", type=str, help="The search query string.")
    args = parser.parse_args()
    
    print(f"Attempting to search Glean datasource 'interviewds' for query: '{args.query}'")
    search_glean(args.query)

if __name__ == "__main__":
    main()
