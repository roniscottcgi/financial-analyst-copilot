import streamlit as st

from langchain_core.tools import tool
from components.ui.ChatUIUtils import toggle_container, display_upload_prompt, append_chat_messages, \
    display_chat_history
from src.service.llm_service import LLMService
from src.utils.factory import get_openai_client, run_read_only_query

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
        if "query_history" not in st.session_state:
            st.session_state.query_history = []
        if "current_executed_sql" not in st.session_state:
            st.session_state.current_executed_sql = None
        if "persist_status_for_rerun" not in st.session_state:
            st.session_state.persist_status_for_rerun = False

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

            # FIX 1: Move the state recovery block INSIDE the chat container layout.
            # If a rerun just occurred, draw the completed static status box right above the answer.
            if st.session_state.persist_status_for_rerun and st.session_state.current_executed_sql:
                with st.status("🤖 Agent executed SQL query", state="complete", expanded=False):
                    st.code(st.session_state.current_executed_sql, language="sql")
                # Immediately reset the gatekeeper so it won't persist across future new chat submissions
                st.session_state.persist_status_for_rerun = False
                st.session_state.current_executed_sql = None

            if assistant_payload:
                with st.chat_message("assistant"):
                        doc_context, schema_context, user_docs_results, db_schema_results = collect_context(new_user_input)

                        @tool
                        def run_database_query(sql_query: str) -> str:
                            """Executes a valid SQL SELECT query against the underlying database tables to extract live figures and rows."""
                            return run_read_only_query(sql_query)

                        tools = [run_database_query]

                        llm_client = get_openai_client()
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

                                    # Set the tracking strings
                                    st.session_state.current_executed_sql = query_to_run

                                    # Show a temporary visual status banner during the heavy network call
                                    with st.status(f"🤖 Agent executing SQL query...", expanded=False) as status:
                                        st.code(query_to_run, language="sql")
                                        live_db_data = run_database_query.invoke(tool_call)
                                        status.update(label="Query complete! Synthesizing data...", state="complete")

                                    langchain_messages.append(live_db_data)

                            # Second Inference Pass: Stream the final answer back to the UI
                            full_response = ""
                            for chunk in llm_client.stream(langchain_messages):
                                if chunk.content:
                                    full_response += chunk.content
                                    placeholder.markdown(full_response)

                            # Append final text response to chat logs
                            append_chat_messages("assistant", full_response)

                            # FIX 2: Tell the next run cycle to explicitly draw the container using our current SQL code
                            if st.session_state.current_executed_sql:
                                st.session_state.persist_status_for_rerun = True

                            # Append to history state (including the SQL query to render later)
                            if doc_context and schema_context and new_user_input and query_to_run and full_response:
                                interation = {
                                    "doc_context": doc_context,
                                    "schema_context": schema_context,
                                    "user_query": new_user_input,
                                    "db_schema_results": db_schema_results,
                                    "user_docs_results": user_docs_results,
                                    "query_to_run": query_to_run,
                                    "assistant_response": full_response,
                                }
                                st.session_state.query_history.append(interation)

                            # Sync the other history component across the app seamlessly
                            st.rerun()
