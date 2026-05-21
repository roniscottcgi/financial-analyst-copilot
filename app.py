import streamlit as st
import httpx

from openai import OpenAI

st.title("Financial Assistant Chat")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(
    http_client=httpx.Client(verify=False),
    api_key=st.secrets["OPENAI_API_KEY"]
)

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

message = [
    {"role": m["role"], "content": m["content"]}
    for m in st.session_state.messages
]

# Display assistant response in chat message container
with st.chat_message("assistant"):
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=message,
        stream=True,
    )
    response = st.write_stream(stream)
st.session_state.messages.append({"role": "assistant", "content": response})