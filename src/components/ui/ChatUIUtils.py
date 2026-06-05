from typing import Any

import streamlit as st
from streamlit.elements.widgets.chat import ChatInputValue


# def collect_assistant_response(message: list[dict[str, Any]]):
#
#     return llm_service.send_request_to_assistant(
#         model=st.session_state["openai_model"],
#         message=message)


def append_chat_messages(role: str, user_input: str | ChatInputValue | list[Any]):
    st.session_state.messages.append({"role": role, "content": user_input})


def display_chat_history():
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def toggle_container() -> bool:
    with st.container(key="toggle_container"):
        col1, col2 = st.columns([3, 1])

        with col1:
            chat_toggle = st.toggle("Show Chat Assistant", key="sidebar_toggle", value=True)

        with col2:
            if chat_toggle and st.session_state.messages:
                if st.button("Clear", key="clear_chat_btn", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()
    return chat_toggle


def display_upload_prompt():
    with st.container():
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.info("💡Upload documents below for RAG-based results.")
        with col2:
            if st.button("✖️", key="exit_banner"):
                st.session_state.show_banner = False
                st.rerun()