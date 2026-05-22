from typing import Any

import streamlit as st
from streamlit.elements.widgets.chat import ChatInputValue

from src.service.llm_service import LLMService


def get_styling():
    st.html("""
             <style>
             .st-key-sidebar_bottom {
                 position: absolute;
                 bottom: 20px;
             }
             </style>
         """)


class ChatUI:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def render(self):
        st.title("Financial Assistant Chat")

        # Initialize chat history
        self.init_history()

        # Create a toggle widget for opening/closing the chat
        with st.container(key="sidebar_bottom"):
            chat_toggle = st.toggle("Show Chat Assistant", key="sidebar_toggle")

        if not chat_toggle:
            st.info("Chat is currently closed. Toggle the switch below to open the chat assistant.")
            return

        # Create a container for the all messages
        chat_container = st.container()

        # Check for new input FIRST (Process data layer before UI layer)
        new_user_input = st.chat_input("How can I assist you?")

        # We will hold the assistant response payload here if one is generated
        assistant_payload = None

        if new_user_input:
            # Save user input to session state immediately so it's part of the history
            st.session_state.messages.append({"role": "user", "content": new_user_input})
            # Prepare the message structure for the LLM
            assistant_payload = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

        with chat_container:
            self.chat_history()

            if assistant_payload:
                with st.chat_message("assistant"):
                    self.handle_assistant_response(assistant_payload)


    def init_history(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def handle_assistant_response(self, message: list[dict[str, Any]]):
        stream = self.llm_service.get_chat_stream(
            model=st.session_state["openai_model"],
            message=message
        )
        response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    def handle_user_input(self, user_input: str | ChatInputValue) -> list[dict[str, Any]]:
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        message = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        return message

    def chat_history(self):
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])