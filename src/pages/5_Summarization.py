import streamlit as st
import openai_connection
import os

st.title("Document Summarization")
if "summarize_prompt" not in st.session_state:
    st.session_state.summarize_prompt = "You are an AI assistant that summarizes markdown text"
    
view_prompt = st.checkbox("View Prompt", value=False)
if view_prompt:
    st.session_state.summarize_prompt = st.text_area("Current Prompt", st.session_state.summarize_prompt)

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