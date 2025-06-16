"""
Streamlit Custom WebSearch Page
This Streamlit page implements a chat interface using an AI Foundry agent for web search capabilities.

Features:
- Uses AI Foundry threads to maintain conversation history
- Displays messages directly from the AI Foundry thread
- Accepts user input via a chat input box
- Sends user input to the AI Foundry agent and processes the response
- Displays both user and assistant messages in the chat interface
- Includes search results from the web

Dependencies:
- streamlit
- openai_connection (custom module for AI Foundry agent interaction)
- azure-ai-projects (Azure AI Projects SDK)
- azure-identity (DefaultAzureCredential)

Session State Keys:
- "ai_foundry_thread_id": ID of the current AI Foundry thread
"""
import streamlit as st
import openai_connection

st.title("Custom WebSearch")
st.write("Ask any question and the AI Foundry agent will search the web to provide an informed answer.")
st.warning("⚠️ Note: This feature currently only works in local deployments due to authentication requirements. Azure web app deployments would require additional configuration.")

# Display thread information and allow creating a new thread
if "ai_foundry_thread_id" in st.session_state:
    with st.expander("Thread Information", expanded=False):
        st.info(f"Using AI Foundry Thread ID: {st.session_state.ai_foundry_thread_id}")
        if st.button("Create New Thread"):
            # Remove the thread ID to create a new one on next search
            del st.session_state.ai_foundry_thread_id
            st.success("New thread will be created on your next search.")
            st.rerun()

# Display current thread messages
if "ai_foundry_thread_id" in st.session_state:
    # Get messages from the existing thread
    with st.spinner("Loading conversation history..."):
        messages = openai_connection.ai_foundry_get_messages(st.session_state.ai_foundry_thread_id)
        
    # Display messages
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# React to user input
if prompt := st.chat_input("What would you like to search for?"):
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process message with AI Foundry agent
    with st.spinner("Searching the web for an answer..."):
        response = openai_connection.ai_foundry_process_message(prompt)
    
    # If we got a response (and not just an error message), display it and refresh
    if response.startswith("Error:"):
        with st.chat_message("assistant"):
            st.error(response)
    else:
        st.rerun()
