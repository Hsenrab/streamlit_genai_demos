"""
Streamlit Custom WebSearch Page
This Streamlit page implements a chat interface using an AI Foundry agent for web search capabilities.

Features:
- Initializes and maintains a chat history in the Streamlit session state
- Provides a prompt management section for customizing the agent's behavior
- Displays all previous chat messages (system, user, assistant) on each rerun
- Accepts user input via a chat input box
- Sends user input and chat history to the AI Foundry agent
- Displays both user and assistant messages in the chat interface
- Updates the chat history after each interaction
- Includes search results from the web

Dependencies:
- streamlit
- openai_connection (custom module for AI Foundry agent interaction)
- utils (custom module for prompt management)
- azure-ai (Azure AI Projects SDK)
- azure-identity (DefaultAzureCredential)

Session State Keys:
- "web_search_messages": List of message dictionaries with "role" and "content" keys
- "ai_foundry_thread_id": ID of the current AI Foundry thread
"""
import streamlit as st
import openai_connection
import utils

st.title("Custom WebSearch")
st.write("Ask any question and the AI Foundry agent will search the web to provide an informed answer.")
st.warning("⚠️ Note: This feature currently only works in local deployments due to authentication requirements. Azure web app deployments would require additional configuration.")

# Display agent and thread information if available
if "ai_foundry_thread_id" in st.session_state:
    with st.expander("Thread Information", expanded=False):
        st.info(f"Using AI Foundry Thread ID: {st.session_state.ai_foundry_thread_id}")
        if st.button("Create New Thread"):
            # Remove the thread ID to create a new one on next search
            if "ai_foundry_thread_id" in st.session_state:
                del st.session_state.ai_foundry_thread_id
            st.success("New thread will be created on your next search.")
            st.rerun()

# Prompt Management Section
with st.expander("Prompt Management", expanded=True):
    st.info("You can customize and save the prompt used for web searching. The changes are saved locally and won't persist in the cloud between redeployments.")
    utils.prompt_management("websearch", "You are an AI assistant that searches the web to provide accurate and up-to-date information.")

# Initialize chat history
if "web_search_messages" not in st.session_state:
    st.session_state.web_search_messages = []
    
    # Get the prompt from session state
    if "websearch_prompt" in st.session_state:
        system_message = st.session_state.websearch_prompt
    else:
        system_message = "You are an AI assistant that searches the web to provide accurate and up-to-date information."
    
    st.session_state.web_search_messages.append({"role": "system", "content": system_message})

# Display chat messages from history on app rerun
for message in st.session_state.web_search_messages:
    if message["role"] != "system":  # Don't display system messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to search for?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.web_search_messages.append({"role": "user", "content": prompt})
    
    # Get response from AI Foundry agent
    response = openai_connection.ai_foundry_web_search(prompt, st.session_state.web_search_messages[:-1])
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.web_search_messages.append({"role": "assistant", "content": response})
