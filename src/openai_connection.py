import openai
import os
import streamlit as st
import urllib.request
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from azure.identity import DefaultAzureCredential

from dotenv import load_dotenv

load_dotenv()

client = openai.AzureOpenAI(
  azure_endpoint = os.getenv("OPENAI_API_ENDPOINT"), 
  api_key=os.getenv("OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

def question(prompt, system_prompt="You are a helpful assistant."):
    """
    Generates a response from the OpenAI GPT-4o model based on a user prompt and an optional system prompt.
    Args:
        prompt (str): The user's input or question to be sent to the language model.
        system_prompt (str, optional): The system-level instruction or context for the assistant. Defaults to "You are a helpful assistant.".
    Returns:
        str: The content of the model's response to the user's prompt.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
    
    
def chat(prompt, history, response_format=None):
    """
    Sends a chat prompt along with conversation history to the OpenAI GPT-4o model and returns the assistant's response.
    Args:
        prompt (str): The latest user input to be sent to the model.
        history (list): A list of previous message dictionaries, each containing 'role' and 'content' keys, representing the conversation history.
        response_format (str, optional): The format for the response. If set to 'json', the API will be instructed
                                         to return a JSON object but the function will still return a string. 
                                         Defaults to None (plain text).
    Returns:
        str: The content of the model's response as a string, or an error message if the request fails.
    Raises:
        None: All exceptions are handled within the function.
    """
    
    messages=history + [{"role": "user", "content": prompt}]
    
    # Set up the API parameters
    params = {
        "model": "gpt-4o",
        "messages": messages
    }
    
    # Add response format if specified
    if response_format == 'json':
        params["response_format"] = {"type": "json_object"}
    
    with st.spinner("Waiting for response..."):
        try:
            response = client.chat.completions.create(**params)
            return response.choices[0].message.content
            
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
            return "Sorry, I am unable to process your request at the moment. The request failed with status code: " + str(error.code)


def generate_markdown(image_url):
    """
    Extracts text content, especially tables, from an image using the GPT-4o model via OpenAI's API.
    The function sends a system prompt instructing the model to extract text and tables from the provided image URL.
    The response is expected to start with the page number and include any detected tables in markdown format,
    followed by a summary or analysis of the extracted content.
    Args:
        image_url (str): The URL of the image from which to extract text and tables.
    Returns:
        str: The extracted content in markdown format, as generated by the GPT-4o model.
    
    """
    
    system_prompt = """
    You are an AI assistance that extracts text from the image. You are especially good at extracting tables.
    Start your response with the page number of the image. 
    If the page contains images extract the text from the image and give a breif descriptioin of the image.
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


def summarize(markdown):
    """
    Summarizes the given markdown text using an AI assistant.
    Args:
        markdown (str): The markdown text to be summarized.
    Returns:
        str: The summarized version of the input markdown text, generated by the AI assistant.
    Notes:
        - Uses a system prompt from Streamlit session state with the key "summarize_prompt".
        - Relies on the `question` function to interact with the AI assistant.
    """
    
    system_prompt = st.session_state.get("summarize_prompt", "You are an AI assistant that summarizes markdown text")
    prompt = f"Input:\n{markdown}"

    return question(prompt, system_prompt)


def compare(markdown1, markdown2):
    """
    Compares two markdown documents using an AI assistant.
    Args:
        markdown1 (str): The first markdown document to compare.
        markdown2 (str): The second markdown document to compare.
    Returns:
        str: The AI-generated comparison result between the two markdown documents.
    Notes:
        - Uses a system prompt from Streamlit session state with the key "comparison_prompt", or a default prompt if not set.
        - Relies on the `question` function to interact with the AI assistant.
    """
    
    system_prompt = st.session_state.get("comparison_prompt", "You are an AI assistant that compares two markdown documents")
    prompt = f"Input:\n\n--- Start of Document 1 ---\n{markdown1}\n--- End of Document 1 ---\n\n--- Start of Document 2 ---\n{markdown2}\n--- End of Document 2 ---"

    return question(prompt, system_prompt)

def ai_foundry_get_messages(thread_id):
    """
    Retrieves and formats messages from an AI Foundry thread.
    
    Args:
        thread_id (str): The ID of the AI Foundry thread.
    
    Returns:
        list: A list of message dictionaries, each containing 'role' and 'content' keys.
    """
    # Get configuration from environment variables
    ai_foundry_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
    ai_foundry_agent_id = os.getenv("AI_FOUNDRY_AGENT_ID")
    
    # Check for required environment variables
    missing_vars = []
    if not ai_foundry_endpoint:
        missing_vars.append("AI_FOUNDRY_ENDPOINT")
    if not ai_foundry_agent_id:
        missing_vars.append("AI_FOUNDRY_AGENT_ID")
    
    if missing_vars:
        return [{"role": "assistant", "content": f"Error: AI Foundry configuration is missing. Please check environment variables: {', '.join(missing_vars)}"}]
    
    try:
        # Initialize the AI Project client
        project = AIProjectClient(
            credential=DefaultAzureCredential(),
            endpoint=ai_foundry_endpoint
        )
        
        # Get messages from the thread
        messages = project.agents.messages.list(
            thread_id=thread_id, 
            order=ListSortOrder.ASCENDING
        )
        
        # Format the messages for display
        formatted_messages = []
        for message in messages:
            if message.text_messages:
                formatted_messages.append({
                    "role": message.role,
                    "content": message.text_messages[-1].text.value
                })
        
        return formatted_messages
        
    except Exception as e:
        return [{"role": "assistant", "content": f"Error: {str(e)}"}]

def ai_foundry_process_message(prompt):
    """
    Sends a user message to the AI Foundry agent, creates or uses an existing thread,
    and processes the message with the agent.
    
    Args:
        prompt (str): The user message to process.
    
    Returns:
        str: Status message indicating success or an error message.
    """
    # Get configuration from environment variables
    ai_foundry_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
    ai_foundry_agent_id = os.getenv("AI_FOUNDRY_AGENT_ID")
    
    # Check for required environment variables
    missing_vars = []
    if not ai_foundry_endpoint:
        missing_vars.append("AI_FOUNDRY_ENDPOINT")
    if not ai_foundry_agent_id:
        missing_vars.append("AI_FOUNDRY_AGENT_ID")
    
    if missing_vars:
        return f"Error: AI Foundry configuration is missing. Please check environment variables: {', '.join(missing_vars)}"
    
    try:
        # Initialize the AI Project client
        project = AIProjectClient(
            credential=DefaultAzureCredential(),
            endpoint=ai_foundry_endpoint
        )
        
        # Get the agent
        agent = project.agents.get_agent(ai_foundry_agent_id)
        
        # Create a new thread if needed or use existing thread
        if "ai_foundry_thread_id" not in st.session_state:
            thread = project.agents.threads.create()
            st.session_state.ai_foundry_thread_id = thread.id
        
        thread_id = st.session_state.ai_foundry_thread_id
        
        # Create a new message with the current prompt
        project.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )
        
        # Run the agent with the message
        run = project.agents.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent.id
        )
        
        # Check run status
        if run.status == "failed":
            return f"Error: Run failed: {run.last_error}"
        
        return "Success"
            
    except Exception as e:
        return f"Error: {str(e)}"

# TODO create button to delete all uploaded pdfs and images.