# code from https://docs.streamlit.io/library/get-started/create-an-app
import os
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import base64
from dotenv import load_dotenv

import openai_connection
import utils


load_dotenv()

st.title('GenAI Demo App')

# Add a button to reset all session state
if st.button("Reset Sessions"):
    for key in st.session_state.keys():
        del st.session_state[key]
        

# Add a button to delete all files in the markdown_output and uploads folders
if st.button("Delete All Uploaded Files"):
    folders_to_clear = ["markdown_output", "uploads"]
    for folder_path in folders_to_clear:
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    st.success("All files in the specified folders have been deleted.")



# Add a button to delete all saved prompts from the prompt folder and its subfolders
if st.button("Delete All Saved Prompts"):
    prompt_folders = ["prompt/comparison", "prompt/summarize"]
    for folder_path in prompt_folders:
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    st.success("All saved prompts have been deleted from the specified folders.")


































































































