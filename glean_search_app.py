#!/usr/bin/env python3
import streamlit as st
import requests
import json
import os
import re

# Configuration
GLEAN_SEARCH_API_ENDPOINT = "https://support-lab-be.glean.com/rest/api/v1/search"  # Updated search endpoint
API_TOKEN = "dummy_placeholder_value"
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
### 📚 Welcome to the Document Search Platform!

This intelligent search application harnesses the power of **Glean's advanced search technology** to help you:

* 🎯 Search through documents in the `interviewds` datasource with precision
* 🚀 Access documents indexed via Glean's powerful Indexing API
* 💫 Experience lightning-fast bulk document processing

> *Powered by Glean's `/indexdocuments` endpoint for optimal performance*
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
# Stylish sidebar header with custom CSS
st.markdown("""
    <style>
    .sidebar-header {
        color: #FF4B4B;
        font-size: 1.3rem;
        font-weight: bold;
    }
    .feature-box {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .example-query {
        background-color: #E8F0FE;
        padding: 0.5rem;
        border-left: 3px solid #1E88E5;
        margin: 0.3rem 0;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.markdown('<p class="sidebar-header">🚀 Glean Search Explorer</p>', unsafe_allow_html=True)
    
    # Interactive feature showcase
    st.markdown("""
    ### ✨ What's Inside
    
    <div class="feature-box">
    Discover the power of Glean's Indexing API:
    
    🔍 **Real-time Search**
    - Lightning-fast document retrieval
    - Smart context understanding
    - Advanced filtering capabilities
    
    📚 **Bulk Processing**
    - Efficient document indexing
    - Automatic metadata extraction
    - Seamless integration
    </div>
    """, unsafe_allow_html=True)

    # Technical Implementation with expandable sections
    with st.expander("🛠️ Technical Stack"):
        st.markdown("""
        ### Core Components
        
        **Backend Magic:**
        ```python
        # Indexing API Integration
        /indexdocuments → Bulk Processing
        /search → Intelligent Queries
        ```
        
        **Frontend Beauty:**
        - 🎯 Streamlit UI
        - 📊 Dynamic Results
        - 🎨 Interactive Elements
        """)

    # Interactive sample queries
    st.markdown("### 🌟 Try These Magic Queries")
    
    # Create clickable sample queries
    sample_queries = [
        ("🤖 AI & Machine Learning", "artificial intelligence"),
        ("📊 Data Science Explorer", "data science techniques"),
        ("🐍 Python Mastery", "python programming best practices"),
        ("📁 Document Deep Dive", "Sample Document 20"),
        ("🎯 Topic Navigator", "Topic 5 analysis")
    ]

    # Make queries interactive
    for label, query in sample_queries:
        if st.button(label, key=f"query_{query}"):
            # You can add functionality to automatically fill the search box
            st.session_state.search_query = query
            st.success(f"Query '{query}' selected!")

    # Add a fun fact section
    st.markdown("""
    ---
    ### 💡 Did You Know?
    """)
    
    # Randomly show different facts
    import random
    facts = [
        "Glean's API can process thousands of documents per minute!",
        "Our search algorithm understands natural language queries.",
        "You can index documents in multiple languages.",
        "Search results are ranked by relevance automatically.",
        "The API supports real-time indexing updates."
    ]
    st.info(random.choice(facts))

    # Add usage statistics (you can make these dynamic)
    st.markdown("""
    ---
    ### 📈 Live Stats
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Indexed Docs", "1.2K", "+123 today")
    with col2:
        st.metric("Search Speed", "0.2s", "-0.1s")

    # Add a feedback section
    st.markdown("---")
    st.markdown("### 🎯 Rate Your Experience")
    rating = st.slider("How helpful was this search?", 1, 5, 5)
    if rating > 3:
        st.success("Thanks for the positive feedback! 🌟")
    elif rating > 0:
        st.info("Thanks! We're working to improve! 💪")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
    Powered by Glean API<br>
    v2.0.0
    </div>
    """, unsafe_allow_html=True)

