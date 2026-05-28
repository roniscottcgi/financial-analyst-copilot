import streamlit as st
from typing import Any

from streamlit.elements.widgets.chat import ChatInputValue

from src.service.llm_service import LLMService

class ChatUI:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def collect_assistant_response(self, message: list[dict[str, Any]]):
        return self.llm_service.send_request_to_assistant(
            model=st.session_state["openai_model"],
            message=message)

    @staticmethod
    def append_chat_messages(role: str, user_input: str | ChatInputValue | list[Any]):
        st.session_state.messages.append({"role": role, "content": user_input})

    @staticmethod
    def display_chat_history():
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def render(self):
        st.title("Financial Assistant Chat")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        with st.container(key="toggle_container"):
            col1, col2 = st.columns([3,1])

            with col1:
                chat_toggle = st.toggle("Show Chat Assistant", key="sidebar_toggle")

            with col2:
                if chat_toggle and st.session_state.messages:
                    if st.button("Clear", key="clear_chat_btn", use_container_width=True):
                        st.session_state.messages = []
                        st.rerun()

        if not chat_toggle:
            st.info("Chat is currently closed. Toggle the chat window to open the chat assistant.")
            return

        chat_container = st.container(height=500, autoscroll=True)
        new_user_input = st.chat_input("How can I assist you?", key="chat_input_key")
        assistant_payload = None

        if new_user_input:
            self.append_chat_messages("user", new_user_input)
            assistant_payload = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

        with chat_container:
            self.display_chat_history()

            if assistant_payload:
                with st.chat_message("assistant"):
                        stream = self.collect_assistant_response(assistant_payload)
                        response = st.write_stream(stream)
                        self.append_chat_messages("assistant", response)