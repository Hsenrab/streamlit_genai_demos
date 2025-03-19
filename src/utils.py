
import fitz
import os
import base64
import streamlit as st

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


def prompt_management(prompt_type, default_prompt):
    
    prompt_folder = f"prompt/{prompt_type}"
    prompt_state = f"{prompt_type}_prompt"
    
    if prompt_state not in st.session_state:
        st.session_state[prompt_state] = default_prompt

    if not os.path.exists(prompt_folder):
        os.makedirs(prompt_folder)
        with open(os.path.join(prompt_folder, "default_prompt.txt"), "w", encoding="utf-8") as f:
            f.write(default_prompt)

    # File selector for prompt.
    prompts = [f for f in os.listdir(prompt_folder) if f.endswith(".txt")]
    selected_file = st.selectbox("Choose a prompt:", prompts)
    if selected_file:
        with open(os.path.join(prompt_folder, selected_file), "r", encoding="utf-8") as f:
            prompt = f.read()

    new_prompt = st.text_area("Prompt", prompt, height=200)
    st.session_state[prompt_state] = new_prompt
    col1, col2 = st.columns(2)

    # Button to save the prompt
    with col1:
        if st.button("Save Prompt"):
            if selected_file:
                # Save to the selected file
                with open(os.path.join(prompt_folder, selected_file), "w", encoding="utf-8") as f:
                    f.write(new_prompt)
                st.success(f"Prompt saved to {selected_file}")
            else:
                st.warning("No file selected to save the prompt.")

    # Button to save as a new prompt
    with col2:
        if st.button("Save as new prompt"):
            new_prompt_name = st.text_input("New Prompt Name (e.g., new_prompt.txt)")
            if new_prompt_name:
                new_prompt_path = os.path.join(prompt_folder, new_prompt_name)
                with open(new_prompt_path, "w", encoding="utf-8") as f:
                    f.write(new_prompt)
                st.success(f"New prompt saved as {new_prompt_name}")
            else:
                st.warning("Please provide a name for the new prompt.")