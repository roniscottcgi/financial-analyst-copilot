import streamlit as st

from src.service.llm_service import LLMService

class ChatUI:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def render(self):
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

        # Only render the chatbot interface if the toggle is set to True
        if chat_toggle:
            # Display chat messages from history on app rerun
            for i, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # React to user input
            if user_input := st.chat_input("How can I assist you?"):
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
                    stream = self.llm_service.get_chat_stream(
                        model=st.session_state["openai_model"],
                        message=message
                    )
                    response = st.write_stream(stream)
                    st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.info("Chat is currently closed. Toggle the switch below to open the chat assistant.")