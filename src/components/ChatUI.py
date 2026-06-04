import streamlit as st

from langchain_core.tools import tool
from components.ui.ChatUIUtils import toggle_container, display_upload_prompt, append_chat_messages, \
    display_chat_history
from src.service.llm_service import LLMService
from src.utils.factory import init_openai_client, run_read_only_query

from utils.vector import append_langchain_messages, collect_context, index_uploaded_files


class ChatUI:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.vector_store = None

    def render(self):
        st.title("Financial Assistant Chat")

        if "show_banner" not in st.session_state:
            st.session_state.show_banner = True
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "indexed_files" not in st.session_state:
            st.session_state.indexed_files = set()

        chat_toggle = toggle_container()

        if not chat_toggle:
            st.info("Chat is currently closed. Toggle the chat window to open the chat assistant.")
            return

        chat_container = st.container(height=500, autoscroll=True)
        new_user_input = st.chat_input("How can I assist you?", key="chat_input_key")
        uploaded_files = st.file_uploader(
            "Upload your data file(s)",
            type=["docx", "pdf"],
            accept_multiple_files=True)

        if uploaded_files:
            with st.spinner("Adding files to store..."):
                self.vector_store, chunks = index_uploaded_files(uploaded_files)
                st.success(f"Successfully indexed {len(chunks)} text chunks into Chroma!")

        if self.vector_store is not None:
            st.markdown(
                '<p style="color: #2ea44f; font-size: 0.85rem; margin: 0;">'
                '<span style="font-size: 1.5rem; vertical-align: middle; padding-right: 4px;">✔</span> '
                'Vector Database Status: Active & Loaded'
                '</p>',
                unsafe_allow_html=True)

        assistant_payload = None

        if new_user_input:
            append_chat_messages("user", new_user_input)
            assistant_payload = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

        with chat_container:
            if st.session_state.show_banner and not uploaded_files:
                display_upload_prompt()

            display_chat_history()

            if assistant_payload:
                with st.chat_message("assistant"):
                    if uploaded_files is None:
                        pass
                        # stream = collect_assistant_response(assistant_payload)
                        # response = st.write_stream(stream)
                        # append_chat_messages("assistant", response)
                    else:
                        doc_context, schema_context = collect_context(new_user_input)

                        @tool
                        def run_database_query(sql_query: str) -> str:
                            """Executes a valid SQL SELECT query against the underlying database tables to extract live figures and rows."""
                            return run_read_only_query(sql_query)

                        tools = [run_database_query]

                        llm_client = init_openai_client()
                        llm_with_tools = llm_client.bind_tools(tools)

                        langchain_messages = append_langchain_messages(doc_context, new_user_input, schema_context)

                        # Let LLM determine intent and possibly make a tool call
                        placeholder = st.empty()
                        with st.spinner("Analyzing request..."):
                            ai_msg = llm_with_tools.invoke(langchain_messages)

                        # Check if the LLM chose to call our Python function
                        if ai_msg.tool_calls:
                            langchain_messages.append(ai_msg)  # Save the tool call request

                            for tool_call in ai_msg.tool_calls:
                                if tool_call["name"] == "run_database_query":
                                    query_to_run = tool_call["args"]["sql_query"]

                                    # Show a status banner in the Streamlit ui so the user knows what query is running
                                    with st.status(f"🤖 Agent executing SQL query...", expanded=False) as status:
                                        st.code(query_to_run, language="sql")
                                        # Trigger our backend database retrieval function
                                        live_db_data = run_database_query.invoke(tool_call)
                                        status.update(label="Query complete! Synthesizing data...", state="complete")

                                    # Append raw rows return packet back to model memory context
                                    langchain_messages.append(live_db_data)

                            # 6. Second Inference Pass: Stream the final answer back to the ui using the fresh rows data
                            full_response = ""
                            for chunk in llm_client.stream(langchain_messages):
                                if chunk.content:
                                    full_response += chunk.content
                                    placeholder.markdown(full_response)

                            append_chat_messages("assistant", full_response)

                        else:
                            # Standard Fallback: The model answered directly without needing live data tools
                            placeholder.markdown(ai_msg.content)
                            append_chat_messages("assistant", ai_msg.content)