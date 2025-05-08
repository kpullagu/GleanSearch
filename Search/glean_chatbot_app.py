#!/usr/bin/env python3
import streamlit as st
import streamlit.components.v1 as components  # Change this line
import requests
import json
import os
import re
import random
from streamlit_chat import message
from datetime import datetime

# Configuration
GLEAN_SEARCH_API_ENDPOINT = "https://glean-be.glean.com/rest/api/v1/search"  # Updated search endpoint
API_TOKEN = "dummy_placeholder_value"
DATASOURCE_NAME = "gleandatasource"
VIEW_URL_BASE = "https://ncbi.nlm.nih.gov/pubmed/"  # Base URL used during indexing
ENABLE_LLM_SUPPORT = os.getenv("ENABLE_LLM_SUPPORT", "false").lower() == "true"

# Page config
st.set_page_config(page_title="Glean Chatbot", page_icon="🤖", layout="wide")

# Custom CSS with improved styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message.user {
        background-color: #E3F2FD;
        border-left: 5px solid #1976D2;
        margin-left: 2rem;
    }
    .chat-message.assistant {
        background-color: #F3E5F5;
        border-left: 5px solid #9C27B0;
        margin-right: 2rem;
    }
    .chat-timestamp {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
        text-align: right;
        font-style: italic;
    }
    .chat-separator {
        margin: 1rem 0;
        border: none;
        border-top: 1px solid rgba(0,0,0,0.1);
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #1976D2;
        color: white;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .search-result {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .search-result:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metadata-tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        background-color: #E8EAF6;
        border-radius: 15px;
        font-size: 0.85em;
        color: #3F51B5;
    }
    .result-title {
        color: #1976D2;
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .result-snippet {
        color: #424242;
        font-size: 0.95em;
        line-height: 1.5;
    }
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

def search_glean_api(query):
    """Performs a search query using the Glean Search API."""
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "datasourcesFilter": [DATASOURCE_NAME],
            "pageSize": 5,
            "includeFields": ["datasource", "metadata", "title", "url", "document", "snippets"]
        }
        
        # Debug print
        print(f"Sending request to: {GLEAN_SEARCH_API_ENDPOINT}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            GLEAN_SEARCH_API_ENDPOINT, 
            headers=headers, 
            json=payload
        )
        
        # Print response status and content for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        # Check response status
        if response.status_code == 200:
            try:
                data = response.json()
                return data, None
            except json.JSONDecodeError as e:
                return None, f"Failed to parse JSON response: {str(e)}"
        else:
            return None, f"API returned status code: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return None, f"Request Error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"

def format_search_response(results):
    """Format search results into a readable response"""
    try:
        if not results:
            return "I couldn't find any relevant information."
        
        # Check if results contains the expected data
        if not isinstance(results, dict):
            return "Received unexpected response format."
            
        # Get results array safely
        search_results = results.get('results', [])
        if not search_results:
            return "No matching documents found."
        
        response = "Here's what I found:\n\n"
        for idx, result in enumerate(search_results[:3], 1):
            try:
                doc = result.get('document', {})
                title = doc.get('title', 'Untitled')
                snippets = result.get('snippets', [])
                snippet_text = snippets[0].get('text', 'No preview available.') if snippets else 'No preview available.'
                
                response += f"📄 **{title}**\n"
                response += f"{snippet_text}\n\n"
            except Exception as e:
                print(f"Error processing result {idx}: {str(e)}")
                continue
        
        return response
    except Exception as e:
        print(f"Error in format_search_response: {str(e)}")
        return "Sorry, I encountered an error processing the search results."

def sidebar_content():
    st.sidebar.title("🚀 Chat Tips")

    st.sidebar.markdown("""
    <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px;'>
    <h4>Try asking about:</h4>

    • Give me opportunities with stage "decisionmakerboughtin"<br>
    • Give me opportunities with stage "appointmentscheduled"<br>
    • Give me all deals which are "CREATED"<br>
    • Latest product specifications<br>
    • Employee onboarding process<br>
    • Company holiday schedule
    </div>
    """, unsafe_allow_html=True)

    tips = [
        "Be specific in your questions",
        "Use keywords related to your topic",
        "Ask about recent documents or policies",
        "Combine topics for detailed insights"
    ]

    st.sidebar.markdown("---")
    st.sidebar.info(f"💡 Tip: {random.choice(tips)}")

    with st.sidebar.expander("ℹ️ About"):
        st.markdown("""
        <div style='background-color: #ffffff; padding: 15px; border-radius: 10px;'>
        <h4>This chatbot interface uses:</h4>

        • Glean Search API for intelligent document search<br>
        • Streamlit for the interactive UI<br>
        • AWS EC2 for robust cloud hosting
        </div>
        """, unsafe_allow_html=True)

    if st.sidebar.button('🗑️ Clear Chat History'):
        st.session_state.messages = []
        st.session_state.search_results = []
        st.experimental_rerun()

def main():
    # Call sidebar content
    sidebar_content()

    # Main Header
    st.markdown("""
    <h1 class="main-header">
        <span style="font-weight:bold; color:black;">🤖 Glean</span>
        <span style="font-weight:normal; color:black;"> Chatbot powered by </span>
        <span style="font-weight:bold; color:#0e4c92;">Streamlit</span>
        <span style="font-weight:normal; color:black;"> on </span>
        <span style="font-weight:bold; color:orange;">Amazon EC2</span>
    </h1>
    <hr style="border:none; height:2px; background:linear-gradient(to right, #ccc, #333, #ccc); margin:0;"/>
    """, unsafe_allow_html=True)

    # Welcome Message
    st.markdown("""
    This intelligent chatbot harnesses the power of **Glean's advanced search technology** to help you:

    * 🎯 Find information across your documents with precision
    * 🚀 Access indexed content instantly
    * 💫 Experience conversational search results
    """)

    # Chat interface
    col1, col2 = st.columns([2, 1])

    with col1:
        # Chat input
        user_input = st.text_input("Ask me anything:", placeholder="e.g., What's our leave policy? What were the Q1 marketing results?")

        if st.button("Send", key="send_button"):
               if user_input:
                # Add user message with timestamp
                current_time = datetime.now().strftime("%H:%M:%S")
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": current_time
                })

                # Perform search with loading indicator
                with st.spinner('🔍 Searching...'):
                    search_results, error = search_glean_api(user_input)

                if error:
                    response = f"❌ Sorry, I encountered an error: {error}"
                else:
                    response = format_search_response(search_results)
                    st.session_state.search_results.append(search_results)

                # Add assistant response with timestamp
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

        # Display chat messages (newest first)
        if st.session_state.messages:
            st.markdown("### 💬 Chat History")

            for idx, msg in enumerate(reversed(st.session_state.messages)):
                with st.container():
                    if msg["role"] == "user":
                        st.markdown(f"""
                            <div class='chat-message user'>
                                <div style='font-weight:bold;'>👤 You:</div>
                                <div style='margin: 8px 0;'>{msg['content']}</div>
                                <div class='chat-timestamp'>{msg['timestamp']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class='chat-message assistant'>
                                <div style='font-weight:bold;'>🤖 Assistant:</div>
                                <div style='margin: 8px 0;'>{msg['content']}</div>
                                <div class='chat-timestamp'>{msg['timestamp']}</div>
                            </div>
                        """, unsafe_allow_html=True)

    # Display detailed search results
    with col2:
        st.markdown("### 📚 Detailed Results")
        if st.session_state.search_results:
            latest_results = st.session_state.search_results[-1]

            for result in latest_results.get('results', []):
                doc = result.get('document', {})
                st.markdown(f"""
                    <div class='search-result'>
                        <div class='result-title'>{doc.get('title', 'Untitled')}</div>
                """, unsafe_allow_html=True)

                # Display metadata if available
                if 'metadata' in doc:
                    st.markdown("**Metadata:**")
                    metadata_html = "".join([
                        f"<span class='metadata-tag'>{key}: {value}</span>"
                        for key, value in doc['metadata'].items()
                        if isinstance(value, (str, int, float))
                    ])
                    st.markdown(metadata_html, unsafe_allow_html=True)

                # Display snippet
                snippet = result.get('snippets', [{'text': 'No preview available.'}])[0].get('text', '')
                st.markdown(f"""
                    <div class='result-snippet'>{snippet}</div>
                """, unsafe_allow_html=True)

                # Display link
                url = doc.get('url', '#')
                st.markdown(f"[View Document]({url})")

                st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:gray;font-size:0.8em;'>Powered by Glean API | © 2024</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
