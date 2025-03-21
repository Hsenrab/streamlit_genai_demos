import openai
import os
import streamlit as st
import urllib.request
import re

from dotenv import load_dotenv

load_dotenv()

def get_available_models():
    """
    Get available models from environment variables.
    Returns a dictionary of model_name: display_name pairs.
    """
    models = {}
    default_model = os.getenv("DEFAULT_MODEL_NAME", "gpt-4o")
    
    # Add the default model
    if default_model:
        models[default_model] = default_model
    
    # Find all model configurations in environment variables
    pattern = r"MODEL_(.+)_NAME"
    for key in os.environ:
        match = re.match(pattern, key)
        if match:
            model_prefix = match.group(1)
            model_name = os.getenv(key)
            if model_name:
                models[model_name] = model_name
    
    return models

def setup_client(model_name=None):
    """
    Set up the Azure OpenAI client using environment variables.
    If model_name is provided, use model-specific credentials.
    """
    try:
        # If model_name is None, get the default model name from environment
        if model_name is None:
            model_name = os.getenv("DEFAULT_MODEL_NAME", "gpt-4o-mini")
        
        # Create prefix for model-specific env vars
        prefix = f"MODEL_{model_name.upper().replace('-', '_')}"
        api_key = os.getenv(f"{prefix}_API_KEY")
        endpoint = os.getenv(f"{prefix}_ENDPOINT")
        api_version = os.getenv(f"{prefix}_API_VERSION", "2024-02-01")
        
        # If model-specific credentials aren't available, fall back to default credentials
        if not api_key or not endpoint:
            api_key = os.getenv("OPENAI_API_KEY")
            endpoint = os.getenv("OPENAI_API_ENDPOINT")
            api_version = "2024-02-01"

        if not api_key or not endpoint:
            st.error(f"Missing API key or endpoint for model: {model_name}")
            return None

        client = openai.AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        return client
    except (ValueError, KeyError, RuntimeError) as e:
        st.error(f"Error setting up Azure OpenAI client: {str(e)}")
        return None


def get_model_params(model_name):
    """Get model-specific parameters"""
    if model_name:
        prefix = f"MODEL_{model_name.upper().replace('-', '_')}"
        deployment_name = os.getenv(f"{prefix}_DEPLOYMENT_NAME", model_name)
        token_param = os.getenv(f"{prefix}_TOKEN_PARAM", "max_tokens")
        unsupported_params = os.getenv(f"{prefix}_UNSUPPORTED_PARAMS", "").lower().split(",")
        return deployment_name, token_param, unsupported_params
    else:
        return os.getenv("DEFAULT_MODEL_NAME", "gpt-4o"), "max_tokens", []

def question(prompt, system_prompt="You are a helpful assistant.", model_name=None, temperature=0.7, max_tokens=1000):
    client = setup_client(model_name)
    if not client:
        return "Failed to initialize OpenAI client."
    
    try:
        deployment_name, token_param, unsupported_params = get_model_params(model_name)
        
        # Base parameters for the API call
        params = {
            "model": deployment_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Add temperature if supported
        if "temperature" not in unsupported_params:
            params["temperature"] = temperature
            
        # Add the appropriate token parameter based on the model
        if token_param == "max_completion_tokens":
            params["max_completion_tokens"] = max_tokens
        else:
            params["max_tokens"] = max_tokens
            
        response = client.chat.completions.create(**params)
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"
    
def chat(prompt, history, model_name=None, temperature=0.7, max_tokens=1000):
    client = setup_client(model_name)
    if not client:
        return "Failed to initialize OpenAI client."
    
    messages = history + [{"role": "user", "content": prompt}]
    
    with st.spinner("Waiting for response..."):
        try:
            deployment_name, token_param, unsupported_params = get_model_params(model_name)
            
            # Base parameters for the API call
            params = {
                "model": deployment_name,
                "messages": messages
            }
            
            # Add temperature if supported
            if "temperature" not in unsupported_params:
                params["temperature"] = temperature
                
            # Add the appropriate token parameter based on the model
            if token_param == "max_completion_tokens":
                params["max_completion_tokens"] = max_tokens
            else:
                params["max_tokens"] = max_tokens
                
            response = client.chat.completions.create(**params)
            result = response.choices[0].message.content
            
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
            result = "Sorry, I am unable to process your request at the moment. The request failed with status code: " + str(error.code)
        except Exception as e:
            result = f"Sorry, I encountered an error: {str(e)}"

    return result

def generate_markdown(image_url, model_name=None, temperature=0.0, max_tokens=2000):
    client = setup_client(model_name)
    if not client:
        return "Failed to initialize OpenAI client."
    
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
    
    try:
        deployment_name, token_param, unsupported_params = get_model_params(model_name)
        
        # Base parameters for the API call
        params = {
            "model": deployment_name,
            "messages": [
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
            ]
        }
        
        # Add temperature if supported
        if "temperature" not in unsupported_params:
            params["temperature"] = temperature
            
        # Add the appropriate token parameter based on the model
        if token_param == "max_completion_tokens":
            params["max_completion_tokens"] = max_tokens
        else:
            params["max_tokens"] = max_tokens
            
        response = client.chat.completions.create(**params)
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

def summarize(markdown, model_name=None, temperature=0.7, max_tokens=1000):
    system_prompt = st.session_state.get("summarize_prompt", "You are an AI assistant that summarizes markdown text")
    prompt = f"Input:\n{markdown}"

    return question(prompt, system_prompt, model_name, temperature, max_tokens)

def compare(markdown1, markdown2, model_name=None, temperature=0.7, max_tokens=1000):
    system_prompt = st.session_state.get("comparison_prompt", "You are an AI assistant that compares two markdown documents")
    prompt = f"Input:\n\n--- Start of Document 1 ---\n{markdown1}\n--- End of Document 1 ---\n\n--- Start of Document 2 ---\n{markdown2}\n--- End of Document 2 ---"

    return question(prompt, system_prompt, model_name, temperature, max_tokens)

# Function to create model selection and parameter UI elements
def create_model_ui(key_prefix=""):
    models = get_available_models()
    model_name = st.selectbox(
        "Select model:",
        options=list(models.keys()),
        key=f"{key_prefix}_model"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            key=f"{key_prefix}_temperature"
        )
    
    with col2:
        max_tokens = st.slider(
            "Max tokens:",
            min_value=100,
            max_value=4000,
            value=1000,
            step=100,
            key=f"{key_prefix}_max_tokens"
        )
    
    return model_name, temperature, max_tokens

# TODO create button to delete all uploaded pdfs and images.
