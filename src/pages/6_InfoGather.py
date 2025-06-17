# filepath: c:\Users\hannahhowell\OneDrive - Microsoft\Documents\Git\streamlit_genai_demos\src\pages\6_InfoGather.py
"""
Streamlit Info Gathering Page
This Streamlit page implements a chat interface that gradually gathers information to build a JSON structure.
Features:
- Initializes and maintains a chat history in the Streamlit session state.
- Maintains a JSON structure that gets updated based on user inputs.
- Displays the conversation in the main panel.
- Displays the current JSON structure in a side panel.
- Uses OpenAI's API to process user inputs and update the JSON structure.
Dependencies:
- streamlit
- openai_connection (custom module for OpenAI API interaction)
- json
Session State Keys:
- "info_gather_messages": List of message dictionaries with "role" and "content" keys.
- "info_json_structure": Dictionary representing the current state of gathered information.
Usage:
- Place this file in the Streamlit app's pages directory.
- Ensure `openai_connection` is implemented and available in the import path.
"""
import streamlit as st
import openai_connection
import json
import utils  # Import utils module to use render_json_section function

# Define the JSON structure template that we want to fill
JSON_STRUCTURE_TEMPLATE = {
    "personal_info": {
        "full_name": "",
        "email": "",
        "phone": "",
        "date_of_birth": ""
    },
    "property_details": {
        "address": "",
        "postcode": "",
        "property_type": "",  # e.g., terraced, semi-detached, detached, flat
        "year_built": "",
        "number_of_bedrooms": "",
        "construction_type": ""  # e.g., brick, stone, timber frame
    },
    "coverage_preferences": {
        "buildings_cover": "",  # Amount in GBP
        "contents_cover": "",   # Amount in GBP
        "accidental_damage": "",  # Yes/No
        "excess_preference": ""  # Amount in GBP
    },
    "risk_factors": {
        "security_system": "",  # Yes/No
        "flood_risk_area": "",  # Yes/No
        "previous_claims": [],
        "listed_building": ""  # Yes/No, Grade I, II, etc.
    }
}

st.subheader("Information Gathering")

# Initialize chat history and JSON structure if they don't exist in session state
if "info_gather_messages" not in st.session_state:
    st.session_state.info_gather_messages = []
    st.session_state.info_gather_messages.append({
        "role": "system", 
        "content": f"""You are an assistant designed to gather information from users. 
        Your goal is to extract structured information and build a JSON object according to this template:
        {json.dumps(JSON_STRUCTURE_TEMPLATE, indent=2)}
        
        Your entire response should be a valid JSON object with the following structure:
        {{
            "message_to_user": "Your conversational message here with follow-up questions",
            "updated_json": [COMPLETE JSON STRUCTURE]
        }}
        
        For example:
        
        {{
            "message_to_user": "Thanks for sharing your name, John! Could you also tell me your email address so we can keep you updated?",
            "updated_json": {{
              "personal_info": {{
                "full_name": "John Smith",
                "email": "",
                "phone": "",
                "date_of_birth": ""
              }},
              "property_details": {{
                "address": "",
                "postcode": "",
                "property_type": "",
                "year_built": "",
                "number_of_bedrooms": "",
                "construction_type": ""
              }}
            }}
        }}
        
        The JSON structure should be built incrementally based on user inputs.
        Make sure the message_to_user is conversational and friendly, and includes follow-up questions.
        Guide the user through filling out each section of the template.
        Don't ask for all information at once - ask one or two questions at a time.
        Always return your ENTIRE response as a single valid JSON object that can be parsed."""
    })
    
    # Store the initial assistant message as a JSON string
    initial_message = json.dumps({
        "message_to_user": "Hi there! I'll help you fill out some information. Let's start by getting your name. What should I call you?",
        "updated_json": {}
    })
    st.session_state.info_gather_messages.append({
        "role": "assistant", 
        "content": initial_message
    })
    
    # Initialize JSON structure
    st.session_state.info_json_structure = {}

# Create a layout with a main panel for chat and a side panel for JSON
main_panel, json_panel = st.columns([2, 1])

with main_panel:    # Display chat messages from history on app rerun
    for message in st.session_state.info_gather_messages:
        if message["role"] != "system":  # Don't display system messages
            with st.chat_message(message["role"]):
                content = message["content"]
                
                # If it's an assistant message, extract the message_to_user part
                if message["role"] == "assistant":
                    try:
                        # Try to parse as JSON
                        parsed_content = json.loads(content)
                        if "message_to_user" in parsed_content:
                            content = parsed_content["message_to_user"]
                    except json.JSONDecodeError:
                        pass  # Keep content as is if parsing fails
                
                st.markdown(content)
                  # React to user input
    if prompt := st.chat_input("Type your response here..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add user message to chat history
        st.session_state.info_gather_messages.append({"role": "user", "content": prompt})        

        # Get model response in JSON format
        with st.spinner("Processing..."):
            response = openai_connection.chat(prompt, st.session_state.info_gather_messages, response_format='json')
        try:
            # Parse the response and extract components
            parsed_response = json.loads(response)
            visible_response = parsed_response.get("message_to_user", "I didn't get that. Could you please try again?")
            st.session_state.info_json_structure = parsed_response.get("updated_json", {})
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(visible_response)
                
            # Add assistant response to chat history (store original JSON string)
            st.session_state.info_gather_messages.append({"role": "assistant", "content": response})
            
        except json.JSONDecodeError:
            # If parsing fails, display an error and store the raw response
            fallback_message = "I'm having trouble processing your response. Let's try again."
            
            with st.chat_message("assistant"):
                st.markdown(fallback_message)
                
            # Store the raw response but add a debug note
            st.session_state.info_gather_messages.append({
                "role": "assistant", 
                "content": json.dumps({
                    "message_to_user": fallback_message,
                    "updated_json": st.session_state.info_json_structure  # Preserve existing structure
                })
            })
            
            st.error("Invalid JSON response received from the model.")

with json_panel:
    st.subheader("Collected Information", divider="gray")
    
    # Display the JSON structure in a user-friendly way
    if st.session_state.info_json_structure:
        # Use the render_json_section function from utils module
        utils.render_json_section(st.session_state.info_json_structure, level=3)
    else:
        st.info("No information collected yet. Start the conversation to gather details.")
        
    # Option to see raw JSON
    with st.expander("View raw JSON"):
        st.json(st.session_state.info_json_structure)    
          # Add a button to reset the information gathering process
    if st.button("Reset Information"):
        # Keep only the system message and add initial assistant message
        system_message = next((msg for msg in st.session_state.info_gather_messages if msg["role"] == "system"), None)
        if system_message:
            st.session_state.info_gather_messages = [system_message]
            
            # Create a string representation of the JSON response
            reset_message = json.dumps({
                "message_to_user": "Let's start over! What's your name?", 
                "updated_json": {}
            })
            
            st.session_state.info_gather_messages.append({
                "role": "assistant", 
                "content": reset_message
            })
        else:
            # Reinitialize if system message not found
            st.session_state.info_gather_messages = []
            st.session_state.info_gather_messages.append({
                "role": "system", 
                "content": f"""You are an assistant designed to gather information from users. 
                Your goal is to extract structured information and build a JSON object according to this template:
                {json.dumps(JSON_STRUCTURE_TEMPLATE, indent=2)}
                
                Your entire response should be a valid JSON object with the following structure:
                {{
                    "message_to_user": "Your conversational message here with follow-up questions",
                    "updated_json": [COMPLETE JSON STRUCTURE]
                }}
                """
            })
            
            # Create a string representation of the JSON response
            reset_message = json.dumps({
                "message_to_user": "Hi there! I'll help you fill out some information. Let's start by getting your name. What should I call you?", 
                "updated_json": {}
            })
            
            st.session_state.info_gather_messages.append({
                "role": "assistant", 
                "content": reset_message
            })
        
        # Reset the JSON structure
        st.session_state.info_json_structure = {}
        st.rerun()