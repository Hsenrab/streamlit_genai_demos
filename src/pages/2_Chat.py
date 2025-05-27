"""
Streamlit Chat Page
This Streamlit page implements a simple chat interface using OpenAI's API.
Features:
- Initializes and maintains a chat history in the Streamlit session state.
- Displays all previous chat messages (system, user, assistant) on each rerun.
- Accepts user input via a chat input box.
- Sends user input and chat history to the OpenAI API via the `openai_connection.chat` function.
- Displays both user and assistant messages in the chat interface.
- Updates the chat history after each interaction.
Dependencies:
- streamlit
- openai_connection (custom module for OpenAI API interaction)
Session State Keys:
- "chat_messages": List of message dictionaries with "role" and "content" keys.
Usage:
- Place this file in the Streamlit app's pages directory.
- Ensure `openai_connection` is implemented and available in the import path.
"""
import streamlit as st
import openai_connection

st.subheader("Chat")
# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
    st.session_state.chat_messages.append({"role": "system", "content": "You are a helpful assistant."})
    
# Display chat messages from history on app rerun
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
            
            
# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    response = openai_connection.chat(prompt, st.session_state.chat_messages)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
        
    # Add assistant response to chat history
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    st.session_state.chat_messages.append({"role": "assistant", "content": response})