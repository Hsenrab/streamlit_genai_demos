import fitz
import os
import base64
import streamlit as st

def pdftoimages(pdf_path):
    """
    Converts each page of a PDF file into an image and saves them locally.
    Args:
        pdf_path (str): The file path to the PDF document to be converted.
    Returns:
        list of str: A list containing the file paths of the generated image files.
    Notes:
        - Images are saved in the 'output_images' directory, which is created if it does not exist.
        - Each image is named using the PDF file name and the page number (e.g., 'document_page0.jpg').
        - Requires the 'fitz' (PyMuPDF) and 'os' modules.
    """
    
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
    """
    Converts an image file to a data URL containing a base64-encoded representation of the image.
    Args:
        image_path (str): The file path to the image.
    Returns:
        str: A data URL string in the format 'data:image/<ext>;base64,<base64_data>' suitable for embedding in HTML.
    Raises:
        FileNotFoundError: If the specified image file does not exist.
        Exception: For other issues encountered while reading or encoding the file.
    Example:
        data_url = create_data_url('path/to/image.png')
    """
    
    binary_fc       = open(image_path, 'rb').read()
    base64_utf8_str = base64.b64encode(binary_fc).decode('utf-8')

    ext= image_path.split('.')[-1]
    dataurl = f'data:image/{ext};base64,{base64_utf8_str}'
    
    return dataurl


def prompt_management(prompt_type, default_prompt):
    """
    Manages prompt selection, editing, and saving for a given prompt type in a Streamlit app.
    This function provides a UI for users to:
    - Select a prompt file from a folder specific to the prompt type.
    - Edit the contents of the selected prompt.
    - Save changes to the existing prompt file.
    - Save the edited prompt as a new file.
    If the prompt folder or default prompt file does not exist, they are created with the provided default prompt.
    Args:
        prompt_type (str): The type/category of the prompt (used to determine the folder and session state key).
        default_prompt (str): The default prompt text to use if no prompt file exists.
    Side Effects:
        - Modifies Streamlit session state to track the current prompt and selected file.
        - Creates directories and files on disk as needed.
        - Updates the UI with Streamlit widgets for prompt management.
    """
    
    prompt_folder = f"prompt/{prompt_type}"
    prompt_state = f"{prompt_type}_prompt"
    
    if prompt_state not in st.session_state:
        st.session_state[prompt_state] = default_prompt
        
    if "prompt_file" not in st.session_state:
        st.session_state.prompt_file = "default_prompt.txt"

    if not os.path.exists(prompt_folder):
        os.makedirs(prompt_folder)
        with open(os.path.join(prompt_folder, "default_prompt.txt"), "w", encoding="utf-8") as f:
            f.write(default_prompt)

    # File selector for prompt.
    prompt_list = [f for f in os.listdir(prompt_folder) if f.endswith(".txt")]
    
    if st.session_state.prompt_file in prompt_list:
        default_index = prompt_list.index(st.session_state.prompt_file)
    else:
        default_index = 0
        
    selected_file = st.selectbox("Choose a prompt:", prompt_list, default_index)
    if selected_file:
        with open(os.path.join(prompt_folder, selected_file), "r", encoding="utf-8") as f:
            st.session_state[prompt_state] = f.read()

    
    new_prompt = st.text_area("Prompt", st.session_state[prompt_state], height=200)
    if new_prompt != st.session_state[prompt_state]:
    
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
                    st.warning("No file selected to save the prompt.")        # Button to save as a new prompt
        with col2:
            display_text = "Save As - Enter New Name (e.g., new_prompt.txt) (no validation for now)"
            new_prompt_name = st.text_input(display_text)
            if new_prompt_name != "":
                new_prompt_path = os.path.join(prompt_folder, new_prompt_name)
                if os.path.exists(new_prompt_path):
                    st.error(f"A file with the name {new_prompt_name} already exists. Please choose a different name.")
                else:
                    with open(new_prompt_path, "w", encoding="utf-8") as f:
                        f.write(new_prompt)
                    st.success(f"New prompt saved as {new_prompt_name}")
                    st.session_state.prompt_file = new_prompt_name
                    st.rerun()
    
def render_json_section(data, level=3):
    """
    Recursively renders a JSON structure in a user-friendly way in Streamlit.
    
    Args:
        data (dict, list): The JSON data to render
        level (int): The heading level for sections (default=3)
    
    Returns:
        None: The function directly renders to the Streamlit UI
        
    Features:
        - Converts keys from snake_case to Title Case
        - Handles nested dictionaries and lists in a compact way
        - Skips empty values
    """
    if isinstance(data, dict):
        # Group simple values and nested structures
        simple_values = {}
        nested_structures = {}
        
        for key, value in data.items():
            if isinstance(value, (dict, list)) and value:  # Skip empty dicts/lists
                nested_structures[key] = value
            elif value not in (None, "", [], {}):  # Only include non-empty simple values
                simple_values[key] = value
        
        # First, display the section name and any simple values in a compact format
        if simple_values:
            values_html = "<div style='margin-bottom:10px;'>"
            for key, value in simple_values.items():
                display_key = key.replace('_', ' ').title()
                values_html += f"<div><strong>{display_key}:</strong> {value}</div>"
            values_html += "</div>"
            st.markdown(values_html, unsafe_allow_html=True)
            
        # Then handle any nested structures with their own sections
        for key, value in nested_structures.items():
            display_key = key.replace('_', ' ').title()
            st.markdown(f"<div style='font-size: 18px; font-weight: bold; margin-top: 10px; margin-bottom: 5px; border-bottom: 1px solid #666;'>{display_key}</div>", unsafe_allow_html=True)
            render_json_section(value, level + 1)
    
    # Handle list values
    elif isinstance(data, list) and data:
        # For simple lists, display items as bullet points
        if all(not isinstance(item, (dict, list)) for item in data):
            items_html = "<ul style='margin-top:0; margin-bottom:10px;'>"
            for item in data:
                items_html += f"<li>{item}</li>"
            items_html += "</ul>"
            st.markdown(items_html, unsafe_allow_html=True)
        # For complex lists with nested structures, process each item recursively
        else:
            for item in data:
                if isinstance(item, (dict, list)):
                    render_json_section(item, level + 1)
                else:
                    st.markdown(f"- {item}")
