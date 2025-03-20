import streamlit as st
import openai_connection

st.subheader("Chat")

# Add model selection UI
with st.expander("Model Settings", expanded=False):
    model_name, temperature, max_tokens = openai_connection.create_model_ui("chat")

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
    st.session_state.chat_messages.append({"role": "system", "content": "You are a helpful assistant."})
    
# Display chat messages from history on app rerun
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
            
            
# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    response = openai_connection.chat(prompt, st.session_state.chat_messages, model_name, temperature, max_tokens)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
        
    # Add assistant response to chat history
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    st.session_state.chat_messages.append({"role": "assistant", "content": response})