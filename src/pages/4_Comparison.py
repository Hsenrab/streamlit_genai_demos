import streamlit as st
import openai_connection
import os
import utils


st.title("Document Comparison")

    
with st.expander("Prompt Management", expanded=True):
    utils.prompt_management("comparison", "You are an AI assistant that compares two documents")


output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

files = [f for f in os.listdir(output_folder)]
selected_files = st.multiselect("Choose two files to compare:", files, max_selections=2)
if len(selected_files) == 2:
    with open(os.path.join(output_folder, selected_files[0]), "r", encoding="utf-8") as f:
        content_1 = f.read()
    with open(os.path.join(output_folder, selected_files[1]), "r", encoding="utf-8") as f:
        content_2 = f.read()
    
    st.text_area("Document Content 1", content_1, height=200)
    st.text_area("Document Content 2", content_2, height=200)
    
    if st.button("Compare"):
        comparison = openai_connection.compare(content_1, content_2)
        st.write(comparison)  
    