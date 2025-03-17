import streamlit as st

st.title("Echo")
st.write("Dummy chat that repeats what you say.")

# Initialize chat history
if "echo_messages" not in st.session_state:
    st.session_state.echo_messages = []
    
# Display chat messages from history on app rerun
for message in st.session_state.echo_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.echo_messages.append({"role": "user", "content": prompt})  
response = f"Echo: {prompt}"
# Display assistant response in chat message container
with st.chat_message("assistant"):
    st.markdown(response)
# Add assistant response to chat history
st.session_state.echo_messages.append({"role": "assistant", "content": response})