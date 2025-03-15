# code from https://docs.streamlit.io/library/get-started/create-an-app

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from vega_datasets import data

st.title('Change Test')

title = os.getenv("TITLE", "Contoso Housing")
logo_image = os.getenv("LOGO_URL", "images/ContosoHousing")

load_dotenv()

# Add a button to reset all session state
if st.button("Reset All"):
    for key in st.session_state.keys():
        del st.session_state[key]


st.title("RAG " + title)

# Add a toggle to select the type of flow
flow_type = st.radio(
    "Select the type of flow:",
    ("Echo", "Chat", "Document Processing")
)

if flow_type == "Echo":
    st.subheader("Echo")
    # Initialize chat history
    if "echo_messages" not in st.session_state:
        st.session_state.echo_messages = []
        
    # Display chat messages from history on app rerun
    for message in st.session_state.echo_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.echo_messages.append({"role": "user", "content": prompt})  
    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.echo_messages.append({"role": "assistant", "content": response})
    
elif flow_type == "Chat":
    st.subheader("Chat")
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        
    # Display chat messages from history on app rerun
    for interaction in st.session_state.chat_messages:
        st.write(interaction)
        if interaction["inputs"]["question"]:
            with st.chat_message("user"):
                st.write(interaction["inputs"]["question"])
        if interaction["outputs"]["answer"]:
            with st.chat_message("assistant"):
                st.write(interaction["outputs"]["answer"])
                
                
    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = "Temp Placeholder"
        
        st.write(response)

    
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response['answer'])
            
        # Add assistant response to chat history
        st.session_state.chat_messages.append(
        {"inputs": {"question": prompt},
         "outputs": {"answer": response['answer']}}
    )


else:
    st.subheader("Document Processing")

    # Input box for pasting text
    document_text = st.text_area("Paste your document text here:")

    # Button to submit the text
    if st.button("Submit"):
        if document_text:
            st.write("Document submitted")
            # Process the document text here
            
            data = {
                "email": document_text
            }
            
            result = {"status": "success", "message": "Placeholder"}
            
            # Display the result from the promptflow processing
            st.json(result)
            
        else:
            st.write("Please paste some text before submitting.")