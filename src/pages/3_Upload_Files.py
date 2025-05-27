"""
3_Upload_Files.py
This Streamlit page provides an interface for uploading and processing files in three formats: PDF, Image, and Text.
- For PDF uploads, users can select the extraction method (GPT 4o or Doc Intelligence), upload a PDF, and extract text from its images using AI models.
- For Image uploads, users can upload an image file and extract text using AI models.
- For Text uploads, users can input text directly and save it as a markdown file.
The extracted or input text is saved as a markdown file in the 'markdown_output' directory. Uploaded files are stored in the 'uploads' directory. The page uses utility functions for file handling and AI-based text extraction.
"""

import streamlit as st
import os
import utils
import openai_connection


st.title("Upload FIles")

# Add a toggle to select the type of flow
upload_type = st.radio(
    "Select the type of upload:",
    ("PDF", "Image", "Text"),
    horizontal=True)
if upload_type == "PDF":
    # File uploader for PDF files
    
    extract_type = st.radio(
    "Select way to extract text from pdf:",
    ("GPT 4o", "Doc Intelligence"),
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
                image_paths = utils.pdftoimages(filepath)
            with st.spinner("Extracting text from images"):
                markdown = ""
                for image_path in image_paths:
                    dataurl = utils.create_data_url(image_path)
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
            
elif upload_type == "Image": 
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
                 
             dataurl = utils.create_data_url(filepath)
             
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
             
else:
    # Text uploader
    document_name = st.text_input("Enter a name for the text:")
    document_text = st.text_area("Enter text:")
    
    # Button to submit the text
    if st.button("Submit"):
        if document_text and document_name:
            # Save the markdown output to a file
            output_folder = "markdown_output"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            output_filename = document_name+"_output.md"
            output_filepath = os.path.join(output_folder, output_filename)
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(document_text)
            st.write(f"Markdown output saved to {output_filepath}")