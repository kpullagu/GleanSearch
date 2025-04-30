#!/usr/bin/env python3
import streamlit as st
import requests
import json
import os
import re

# Configuration
GLEAN_SEARCH_API_ENDPOINT = "https://support-lab-be.glean.com/rest/api/v1/search"  # Updated search endpoint
API_TOKEN = os.environ.get('API_TOKEN')  # Token provided by user
DATASOURCE_NAME = "interviewds"
VIEW_URL_BASE = "https://ncbi.nlm.nih.gov/pubmed/"  # Base URL used during indexing

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# --- API Search Logic ---
@st.cache_data(ttl=600)  # Cache results for 10 minutes
def search_glean_api(query):
    """Performs a search query using the Glean Search API."""
    payload = {
        "query": query,
        "datasourcesFilter": [DATASOURCE_NAME],  # Filter by our specific datasource
        "pageSize": 10,  # Limit the number of results per page
        "includeFields": ["datasource", "metadata", "title", "url", "document"],
        "pageToken": None  # Optional: For pagination, set the token for the next page
    }
    
    st.write(f"Sending API search request for query: '{query}'...")
    
    try:
        response = requests.post(GLEAN_SEARCH_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        st.write(f"API Search request successful. Status: {response.status_code}")
        search_results = response.json()
        return search_results, None  # Return results and no error
    except requests.exceptions.RequestException as e:
        st.error(f"Error submitting API search request: {e}")
        error_details = f"Error: {e}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_details += f"\nStatus: {e.response.status_code}\nContent: {e.response.json()}"
            except json.JSONDecodeError:
                error_details += f"\nStatus: {e.response.status_code}\nContent: {e.response.text}"
        st.error(error_details)
        return None, str(e)  # Return no results and error string
    except json.JSONDecodeError:
        st.warning("Error decoding JSON response from search API.")
        return None, "JSONDecodeError"

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("Glean Document Search (Datasource: interviewds)")
# Add a custom image to the header
st.image("header_image-1.jpg", caption="Glean Document Search", use_container_width=True)


st.markdown("""
This application allows you to search documents indexed in the Glean platform for the `interviewds` datasource.
The documents were indexed using the Glean Indexing API with the `/indexdocuments` bulk endpoint.
""")

query = st.text_input("Enter your search query:", placeholder="e.g., Sample Document, machine learning, Topic 5")

if st.button("Search"):
    if query:
        with st.spinner("Searching..."):
            results_data, error = search_glean_api(query)
            
            st.subheader("Search Results")
            if results_data and results_data.get("results"):
                results_list = results_data["results"]
                st.success(f"Found {len(results_list)} results.")
                for i, result in enumerate(results_list):
                    st.markdown(f"**Result {i+1}**")
                    doc = result.get("document", {})
                    title = doc.get("title", "N/A")
                    url = doc.get("url") or f"{VIEW_URL_BASE}{doc.get('id', '')}"
                    snippets = result.get("snippets", [])
                    first_snippet_text = snippets[0].get("text", "No snippet available.") if snippets else "No snippet available."
                    snippet = first_snippet_text
                    
                    st.markdown(f"**[{title}]({url})**")
                    st.markdown(f"_URL: {url}_ ")
                    st.markdown(f"Body Snippet: {snippet}")
                    st.divider()
            else:
                st.info("No results found for your query.")
    else:
        st.warning("Please enter a search query.")

# Add information about the implementation
st.sidebar.title("About")
st.sidebar.info("""
### Glean Indexing API Demo

This application demonstrates the use of Glean's Indexing API to:
1. Index sample documents using the `/indexdocuments` bulk endpoint
2. Search the indexed documents via search API.

The implementation includes:
- Python script for bulk document indexing
- Streamlit UI for searching indexed documents.
""")

# Add sample queries
st.sidebar.title("Sample Queries")
st.sidebar.markdown("""
Try these sample queries:
- Topic 5
- Sample Document 20
- artificial intelligence
- data science
- python programming
""")
