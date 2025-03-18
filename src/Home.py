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








































































































