"""
5_Summarization.py
This Streamlit page provides a user interface for summarizing markdown documents using an AI assistant.
Users can select a markdown file from the 'markdown_output' directory, view its content, and generate a summary
using an AI model via the `openai_connection` module. The page also includes a prompt management section for
customizing the summarization prompt.
Purpose:
- Allow users to easily select and summarize markdown documents.
- Display the original document content for reference.
- Integrate prompt management for flexible summarization instructions.
"""

import streamlit as st
import openai_connection
import os
import utils

st.title("Document Summarization")
st.write("Use this page to generate AI-powered summaries of documents that were previously uploaded and processed through the Upload Files page. The AI will identify and condense the key information from your document.")

with st.expander("Prompt Management", expanded=True):
    st.info("You can customize and save the prompt used for document summarization. The changes are saved locally and won't persist in the cloud between redeployments.")
    utils.prompt_management("summarize", "You are an AI assistant that summarizes markdown documents")

output_folder = "markdown_output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
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