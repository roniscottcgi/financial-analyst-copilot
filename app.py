import streamlit as st
import httpx

from openai import OpenAI

# Set OpenAI API key from Streamlit secrets
client = OpenAI(
    http_client=httpx.Client(verify=False),
    api_key=st.secrets["OPENAI_API_KEY"]
)

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Expand the page to full width
st.set_page_config(layout="wide")

# Create columns (adjust ratios to fit your needs)
left_sidebar, main_content, right_sidebar = st.columns([2, 4, 2], border=True)

# Add elements to the left sidebar
with left_sidebar:
    st.title("History Section")
    st.write("Here is the history of queries and there responses")

# Add elements to the main content
with main_content:
    # Sub-columns to create margins: 1 part empty, 2 parts content, 1 part empty
    empty_left, center_content, empty_right = st.columns([1, 2, 1])

    with center_content:
        st.header("Main Centered Section")
        st.write("This content is perfectly centered within the main area")

# Add elements to your right sidebar
with right_sidebar:
    st.title("Financial Assistant Chat")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create a toggle widget for opening/closing the chat
    with st.container(key="sidebar_bottom"):
        chat_toggle = st.toggle("Show Chat Assistant", key="sidebar_toggle")

    st.html("""
             <style>
             .st-key-sidebar_bottom {
                 position: absolute;
                 bottom: 20px;
             }
             </style>
         """)

    # chat_toggle = st.toggle("Show Chat Assistant", value=True)

    # Only render the chatbot interface if the toggle is set to True
    if chat_toggle:
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if user_input := st.chat_input("What is up?"):
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(user_input)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})

        message = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            if message:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=message,
                    stream=True,
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("Chat is currently closed. Toggle the switch below to open the chat assistant.")