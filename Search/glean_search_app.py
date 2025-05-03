#!/usr/bin/env python3
import streamlit as st
import requests
import json
import os
import re
import random

# Configuration
GLEAN_SEARCH_API_ENDPOINT = "https://glean-be.glean.com/rest/api/v1/search"  # Updated search endpoint
API_TOKEN = "dummy_placeholder_value"
DATASOURCE_NAME = "gleandatasource"
VIEW_URL_BASE = "https://ncbi.nlm.nih.gov/pubmed/"  # Base URL used during indexing

# Predefined search categories and queries
SEARCH_CATEGORIES = {
    "HR Documents": {
        "description": "Search HR policies, guidelines, and documents",
        "sample_queries": [
            "leave policy",
            "employee benefits",
            "HR guidelines",
            "work from home policy",
            "performance review",
            "sick leave",
            "vacation policy"
        ]
    },
    "Marketing Materials": {
        "description": "Search marketing reports, campaigns, and analytics",
        "sample_queries": [
            "marketing ROI",
            "campaign performance",
            "Q1 2024 marketing",
            "digital marketing",
            "social media analytics",
            "email campaigns",
            "marketing metrics"
        ]
    },
    "Engineering Docs": {
        "description": "Search technical documentation and guides",
        "sample_queries": [
            "system design",
            "technical architecture",
            "engineering guidelines",
            "code review",
            "development process",
            "technical specs"
        ]
    }
}


headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# --- API Search Logic ---
@st.cache_data(ttl=600)
def search_glean_api(query):
    """Performs a search query using the Glean Search API."""
    payload = {
        "query": query,
        "datasourcesFilter": [DATASOURCE_NAME],
        "pageSize": 10,
        "includeFields": ["datasource", "metadata", "title", "url", "document", "customProperties", "tags"],
        "pageToken": None
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

# Page Configuration
st.set_page_config(layout="wide", page_title="Enhanced Glean Search")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .block-container {
        padding-top: 1rem;
    }
    .search-results {
        margin-top: 2rem;
    }
    .result-box {
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .sidebar-content {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<h1 class="main-header">
    <span style="font-weight:bold; color:black;">📚 Glean</span>
    <span style="font-weight:normal; color:black;"> search powered by </span>
    <span style="font-weight:bold; color:#0e4c92;">Streamlit</span>
    <span style="font-weight:normal; color:black;"> on </span>
    <span style="font-weight:bold; color:orange;">Amazon EC2</span>
</h1>
<hr style="border:none; height:2px; background:linear-gradient(to right, #ccc, #333, #ccc); margin:0;"/>
""", unsafe_allow_html=True)

# Welcome Message
st.markdown("""
This intelligent search application harnesses the power of **Glean's advanced search technology** to help you:

* 🎯 Search through documents with precision
* 🚀 Access indexed documents instantly
* 💫 Experience lightning-fast results
""")

# Search Interface
query = st.text_input("Enter your search query:", placeholder="e.g., Sample Document, leave policy, marketing campaign, technical specs, Topic 5")

# Process Search
if st.button("Search"):
    if query:
        with st.spinner("Searching..."):
            results_data, error = search_glean_api(query)

            st.subheader("Search Results")
            if results_data and results_data.get("results"):
                results_list = results_data["results"]
                st.success(f"Found {len(results_list)} results.")
                for i, result in enumerate(results_list):
                    doc = result.get("document", {})
                    metadata = result.get("metadata", {})
                    title = doc.get("title", "Untitled")
                    url = doc.get("url", VIEW_URL_BASE)
                    snippet = result.get("snippets", [{'text': 'No preview available.'}])[0].get('text', 'No preview available.')

                    # Display result details
                    st.markdown(f"""
                    <div class="result-box">
                        <h3>Title: {title}</h3>
                        <p><strong>Body:</strong> <em>{snippet}</em></p>
                        <p><a href="{url}" target="_blank">View Document</a></p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display raw API response for doc and metadata
                    #with st.expander(f"Raw API Response for Result {i+1}"):
                    #    st.json({"document": doc, "metadata": metadata})

                    st.divider()
            else:
                st.info("No results found for your query.")
    else:
        st.warning("Please enter a search query.")

# Sidebar Content
with st.sidebar:
    st.markdown("### 🚀 Search Tips")
    
    # Example Queries
    st.markdown("""
    Try these examples:
    - Sample Document 20
    - Topic 5
    - Author: KPull AND department": "Human Resources"
    - policy_type:Career AND tags:Employee
    - Author: Kpull
    - Author: KPull AND Marketing
    - topic: Campaign ROI Analysis: Social Media vs Email
    """)
    
    # Random Tips
    tips = [
        "Use quotes for exact matches",
        "Try specific document numbers",
        "Combine multiple search terms",
        "Use descriptive keywords"
    ]
    
    st.info(f"💡 Tip: {random.choice(tips)}")
    
    # About Section
    with st.expander("ℹ️ About"):
        st.markdown("""
        This search interface uses:
        - Glean Search API
        - Streamlit Framework
        - AWS EC2 hosting
        """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;font-size:0.8em;'>Powered by Glean API</p>",
    unsafe_allow_html=True
)
