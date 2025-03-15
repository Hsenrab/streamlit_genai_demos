# code from https://docs.streamlit.io/library/get-started/create-an-app
import os
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import base64
from dotenv import load_dotenv

import openai_connection

load_dotenv()

st.title('Change Test')

title = os.getenv("TITLE", "Contoso Housing")
logo_image = os.getenv("LOGO_URL", "images/ContosoHousing")



# Add a button to reset all session state
if st.button("Reset All"):
    for key in st.session_state.keys():
        del st.session_state[key]


st.title("Demos" + title)

# Add a toggle to select the type of flow
flow_type = st.radio(
    "Select the type of flow:",
    ("Echo", "Chat", "Text Extraction", "Document Summarization", "Document Comparison"),
    horizontal=True
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
    
elif flow_type == "Text Extraction":
    st.subheader("Text Extraction")
    # Add a toggle to select the type of flow
    upload_type = st.radio(
        "Select the type of upload:",
        ("PDF", "Image"),
        horizontal=True)

    if upload_type == "PDF":
        # File uploader for PDF files
        
        extract_type = st.radio(
        "Select way to extract text from pdf:",
        ("Doc Intelligence", "GPT 4o"),
        horizontal=True)
        
        document_file = st.file_uploader("Upload a PDF file:")
        if document_file:
            # Create uploads folder if it does not already exist
            if not os.path.exists("uploads"):
                os.makedirs("uploads")
            
            filepath = os.path.join("uploads", document_file.name)
            with open(filepath, "wb") as f:
                f.write(document_file.getbuffer())
        
        # Button to submit the file
        if st.button("Submit"):
            if extract_type == "Doc Intelligence":
                st.write("Not yet implemented")
            else:
                with st.spinner("Converting to Images"):
                    image_paths = openai_connection.pdftoimages(filepath)
                with st.spinner("Extracting text from images"):
                    markdown = ""
                    for image_path in image_paths:
                        dataurl = openai_connection.create_data_url(image_path)
                        result = openai_connection.generate_markdown(dataurl)
                        markdown += result
                st.write(markdown)
                # Save the markdown output to a file
                output_folder = "markdown_output"
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                output_filename = os.path.splitext(document_file.name)[0] + "_output.md"
                output_filepath = os.path.join(output_folder, output_filename)

                with open(output_filepath, "w", encoding="utf-8") as f:
                    f.write(markdown)

                st.write(f"Markdown output saved to {output_filepath}")
    else: # Image
        # File uploader for images
        document_image = st.file_uploader("Upload an image file:")
        
        # Button to submit the image
        if st.button("Submit"):
            if document_image:
                # Write the uploaded image to a file
                st.write("Image submitted")
                
                # Create uploads folder if it does not already exist
                if not os.path.exists("uploads"):
                    os.makedirs("uploads")
                
                filepath = os.path.join("uploads", document_image.name)
                with open(filepath, "wb") as f:
                    f.write(document_image.getbuffer())
                    
                dataurl = openai_connection.create_data_url(filepath)
                
                result = openai_connection.generate_markdown(dataurl)
                st.write(result)
                # Save the markdown output to a file
                output_folder = "markdown_output"
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                output_filename = os.path.splitext(document_image.name)[0] + "_output.md"
                output_filepath = os.path.join(output_folder, output_filename)

                with open(output_filepath, "w", encoding="utf-8") as f:
                    f.write(result)

                st.write(f"Markdown output saved to {output_filepath}")
            
elif flow_type == "Document Summarization":
    st.subheader("Document Summarization")
    
    # File selector for markdown files
    markdown_files = [f for f in os.listdir("markdown_output") if f.endswith(".md")]

    selected_file = st.selectbox("Choose a markdown file to summarize:", markdown_files)

    if selected_file:
        with open(os.path.join("markdown_output", selected_file), "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        st.text_area("Document Content", markdown_content, height=400, disabled=True)
        
        if st.button("Summarize"):
            summary = openai_connection.summarize(markdown_content)
            st.write(summary)
    
else: # Document Comparison
    # File selector for markdown files
    markdown_files = [f for f in os.listdir("markdown_output") if f.endswith(".md")]

    selected_files = st.multiselect("Choose two markdown files to compare:", markdown_files, max_selections=2)

    if len(selected_files) == 2:
        with open(os.path.join("markdown_output", selected_files[0]), "r", encoding="utf-8") as f:
            markdown_content_1 = f.read()
        with open(os.path.join("markdown_output", selected_files[1]), "r", encoding="utf-8") as f:
            markdown_content_2 = f.read()
        
        st.text_area("Document Content 1", markdown_content_1, height=200)
        st.text_area("Document Content 2", markdown_content_2, height=200)
        
        if st.button("Compare"):
            comparison = openai_connection.compare(markdown_content_1, markdown_content_2)
            st.write(comparison)  

    