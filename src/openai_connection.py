import openai
import os
import streamlit as st
import urllib.request

from dotenv import load_dotenv

load_dotenv()

client = openai.AzureOpenAI(
  azure_endpoint = os.getenv("OPENAI_API_ENDPOINT"), 
  api_key=os.getenv("OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

def question(prompt, system_prompt="You are a helpful assistant."):

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    print(response.choices[0].message.content)
    
    
def chat(prompt, history):
    
    messages=history + [{"role": "user", "content": prompt}]

    
    with st.spinner("Waiting for response..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )

            result = response.choices[0].message.content
            
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))

            result = "Sorry, I am unable to process your request at the moment. The request failed with status code: " + str(error.code)

    return result

