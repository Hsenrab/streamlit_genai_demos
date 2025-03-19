import streamlit as st
import openai_connection
import os
import utils

st.title("Document Summarization")

with st.expander("Prompt Management", expanded=True):
    utils.prompt_management("summarize", "You are an AI assistant that summarizes documents")

output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
# File selector for files
files = [f for f in os.listdir(output_folder)]
selected_file = st.selectbox("Choose a file to summarize:", files)
if selected_file:
    with open(os.path.join(output_folder, selected_file), "r", encoding="utf-8") as f:
        content = f.read()
    
    st.text_area("Document Content", content, height=400, disabled=True)
    
    if st.button("Summarize"):
        summary = openai_connection.summarize(content)
        st.write(summary)