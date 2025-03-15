import openai
import os
import streamlit as st
import urllib.request

import fitz
import base64


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

    return response.choices[0].message.content
    
    
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


def generate_markdown(image_url):
    """
    Gpt-4o model
    """
    
    system_prompt = """
    You are an AI assistance that extracts text from the image. You are especially good at extracting tables.
    Start your response with the page number of the image. 
    Example Page:
    
    Page 123
    
    Monthly Savings
    | Month    | Savings |Details      |
    | -------- | ------- |------------ |
    | January  | $250    | for holiday |
    | February | $80     | pension     |
    | March    | $420    | new cat     |
    
    Savings were significantly lower in February. This is surprising because it is a short month and contributing to pension shuld be a priority.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract text from the image"},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            },
        ],
        max_tokens=2000,
        temperature=0.0,
    )
    
    return response.choices[0].message.content


def pdftoimages(pdf_path):
    
    pdf_document = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        
        # Save image locally
        output_dir = "output_images"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        image_path = os.path.join(output_dir, f'{pdf_name}_page{page_num}.jpg')
        pix.save(image_path)
        
        image_paths.append(image_path)
        
    return image_paths


def create_data_url(image_path):
    binary_fc       = open(image_path, 'rb').read()
    base64_utf8_str = base64.b64encode(binary_fc).decode('utf-8')

    ext= image_path.split('.')[-1]
    dataurl = f'data:image/{ext};base64,{base64_utf8_str}'
    
    return dataurl


def summarize(markdown):
    system_prompt = "You are an AI assistant that summarizes markdown text"
    prompt = f"Text to summarize:\n{markdown}"

    return question(prompt, system_prompt)


def compare(markdown1, markdown2):
    system_prompt = "You are an AI assistant that copmares two markdown documents"
    prompt = f"Text to Compare:\n\n--- Start of Document 1 ---\n{markdown1}\n--- End of Document 1 ---\n\n--- Start of Document 2 ---\n{markdown2}\n--- End of Document 2 ---\n\n--- End of Comparison ---"

    return question(prompt, system_prompt)

# TODO create button to delete all uploaded pdfs and images.