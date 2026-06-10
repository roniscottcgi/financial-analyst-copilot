import streamlit as st

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, content, BaseMessage

from components.ui.ChatUIUtils import toggle_container, display_upload_prompt, append_chat_messages, \
    display_chat_history
from src.service.llm_service import LLMService
from src.utils.factory import get_openai_client, run_read_only_query

from utils.vector import form_prompt, collect_context_from_vector_store, index_uploaded_files_to_vector_store


class ChatUI:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.vector_store = None

    def render(self):
        st.title("Financial Assistant Chat")

        self.init_session_state()

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

        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]

        if len(uploaded_files) != st.session_state.uploaded_files_size:
            progress_bar = st.progress(0, text="Starting indexing...")

            # Track variables outside the loop to catch them when the generator finishes
            vector_store = None
            chunks = []

            for current, total, v_store, all_chunks in index_uploaded_files_to_vector_store(uploaded_files):
                percent = int((current / total) * 100)
                progress_bar.progress(percent, text=f"Processing file ({current}/{total})")

                # These will overwrite with the actual objects on the final yield
                if v_store is not None:
                    vector_store = v_store
                    chunks = all_chunks

            # Save to session state AFTER the loop finishes
            st.session_state.vector_store = vector_store
            st.session_state.uploaded_files_size = len(chunks)

            progress_bar.empty()
            if chunks:
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

            # Maintain query status on reruns
            if st.session_state.persist_status_for_rerun and st.session_state.current_executed_sql:
                with st.status(":material/smart_toy: Agent executed SQL query", state="complete", expanded=False):
                    st.code(st.session_state.current_executed_sql, language="sql")
                st.session_state.persist_status_for_rerun = False
                st.session_state.current_executed_sql = None

            if assistant_payload:
                with st.chat_message("assistant"):
                    schema_context, db_schema_results = "", [],
                    doc_context, user_docs_results = "", []

                    # TOOL 2: This tool ONLY extracts database schema tables/columns
                    @tool
                    def fetch_database_schema(search_query: str) -> str:
                        """Retrieves the relational database schema layouts, tables, and column metadata match definitions.
                        ALWAYS call this tool first before generating SQL to verify which tables and columns exist."""
                        nonlocal schema_context, db_schema_results
                        # Pull everything, but we ONLY extract and give the model the database layouts
                        schema_context, db_schema_results = collect_context_from_vector_store("db_schema", search_query)
                        return f"--- AVAILABLE DATABASE SCHEMA MATCHES ---\n{schema_context}"

                    @tool
                    def run_database_query(sql_query: str) -> str:
                        """Executes a valid SQL SELECT query against the underlying database tables to extract live figures and rows.
                        ONLY invoke this tool if the user's query directly relates to the financial metrics or tables explicitly listed in the schema context.
                        DO NOT use this tool for general knowledge, weather, greetings, or topics outside of this database."""
                        try:
                            return run_read_only_query(sql_query)
                        except Exception as e:
                            return f"SQL Execution Error: {str(e)}. Please correct your syntax or window function design and try again."

                    tools = [fetch_database_schema, run_database_query]

                    # TOOL 1: This tool ONLY extracts text from uploaded PDFs/Word docs
                    if uploaded_files:
                        @tool
                        def search_uploaded_documents(search_query: str) -> str:
                            """Searches the user's uploaded text files, financial documents, and PDFs for relevant text matches.
                            ONLY call this tool if the user's question can be answered by reading their uploaded documents."""
                            nonlocal doc_context, user_docs_results
                            # Pull everything, but we ONLY extract and give the model the document text
                            doc_context, user_docs_results = collect_context_from_vector_store("user_documents",
                                                                                               search_query)
                            return f"--- USER DOCUMENT CONTENT ---\n{doc_context}"

                        tools.append(search_uploaded_documents)

                    llm_client = get_openai_client()

                    # Bind query tool to chat model
                    llm_with_tools = llm_client.bind_tools(tools)

                    # 4. AGENTIC INSTRUCTIONS PROMPT (Weather escape hatch included)
                    system_instruction = (
                        "You are a helpful Financial Assistant. You have access to tools that can pull data layouts, "
                        "read internal text documents, and execute SQL statements.\n\n"
                        "OPERATIONAL RULES:\n"
                        "1. If asked a data query, you do not know the database schemas initially. Call 'fetch_database_schema' "
                        "first to pull the structural metadata formats.\n"
                        "2. Once you receive the table data layouts from that tool, generate your valid SQL and call 'run_database_query'.\n"
                        "3. If a user asks specifically about information inside their uploaded files, call 'search_uploaded_documents'.\n"
                        "4. CRITICAL: If the user request is completely unrelated to finance, portfolios, or data (e.g. weather, general chit-chat), "
                        "5. CRITICAL DATABASE COMPATIBILITY: Avoid using complex window functions like LAG(), LEAD(), or PARTITION BY "
                            "unless absolutely necessary. Favor standard aggregations (SUM, AVG, COUNT, GROUP BY) to maximize query stability."
                        "DO NOT call any tools. Answer directly using your general knowledge, or politely decline if appropriate."
                    )

                    langchain_messages: list[BaseMessage] = [SystemMessage(content=system_instruction)]
                    for m in st.session_state.messages:
                        if m["role"] == "user":
                            langchain_messages.append(HumanMessage(content=m["content"]))
                        elif m["role"] == "assistant":
                            # Distinguish between tool execution calls and raw response layouts
                            if isinstance(m.get("content"), list) or "tool_calls" in m:
                                langchain_messages.append(
                                    AIMessage(content=m.get("content", ""), tool_calls=m.get("tool_calls", []))
                                )
                            else:
                                langchain_messages.append(AIMessage(content=m["content"]))
                        elif m["role"] == "tool":
                            langchain_messages.append(
                                ToolMessage(content=m["content"], tool_call_id=m["tool_call_id"])
                            )

                    # Append current user input
                    langchain_messages.append(HumanMessage(content=str(new_user_input)))

                    with st.spinner("Processing request..."):
                        placeholder = st.empty()
                        ai_msg = llm_with_tools.invoke(langchain_messages)  # Invoke request

                        query_to_run = ""

                        # 3-TURN SEQUENTIAL CONTEXT AUTO-CORRECTION LOOP
                        for loop_turn in range(3):
                            if not ai_msg.tool_calls:
                                break

                            # Step A: Append the tracking instruction containing the tool generation request
                            langchain_messages.append(ai_msg)

                            # Step B: Dynamically extract ALL tool call requests generated on this turn
                            current_calls = ai_msg.tool_calls if isinstance(ai_msg.tool_calls, list) else [
                                ai_msg.tool_calls]

                            # Step C: Loop over each call in this turn to respond to every requested ID sequentially
                            for tool_call in current_calls:

                                # CASE 1: Processing text matches from files
                                if tool_call["name"] == "search_uploaded_documents":
                                    context_raw = search_uploaded_documents.invoke(tool_call)
                                    langchain_messages.append(
                                        ToolMessage(content=str(context_raw), tool_call_id=tool_call["id"]))

                                # CASE 2: Processing layout contexts from schema
                                elif tool_call["name"] == "fetch_database_schema":
                                    context_raw = fetch_database_schema.invoke(tool_call)
                                    langchain_messages.append(
                                        ToolMessage(content=str(context_raw), tool_call_id=tool_call["id"]))

                                # CASE 3: Executing final SQL compilation queries
                                elif tool_call["name"] == "run_database_query":
                                    query_to_run = tool_call["args"].get("sql_query", "")
                                    st.session_state.current_executed_sql = query_to_run

                                    with st.status("🤖 Agent executing SQL query...", expanded=False) as status:
                                        st.code(query_to_run, language="sql")
                                        context_raw = run_database_query.invoke(tool_call)

                                        if "SQL Execution Error" in str(context_raw):
                                            status.update(
                                                label="SQL syntax error detected. Retrying auto-correction...",
                                                state="running")
                                        else:
                                            status.update(label="Query complete! Synthesizing findings...",
                                                          state="complete")

                                    langchain_messages.append(
                                        ToolMessage(content=str(context_raw), tool_call_id=tool_call["id"]))

                                ai_msg = llm_with_tools.invoke(langchain_messages)

                    # 1. Capture the full text that was already generated inside the loop
                    full_response = ai_msg.content

                    # 2. If full_response is empty (meaning no tools were used, like a weather query),
                    # fall back to streaming it cleanly
                    if not full_response:
                        full_response = ""
                        for chunk in llm_client.stream(langchain_messages):
                            if chunk.content:
                                full_response += chunk.content
                                placeholder.markdown(full_response)
                    else:
                        # Display the completed financial response instantly
                        placeholder.markdown(full_response)

                    # 3. Save to chat and handle session states
                    append_chat_messages("assistant", full_response)

                    if st.session_state.current_executed_sql:
                        st.session_state.persist_status_for_rerun = True

                    # 4. Save to historical logs dictionary
                    interaction = {
                        "doc_context": doc_context or None,
                        "schema_context": schema_context or None,
                        "user_query": new_user_input or None,
                        "db_schema_results": db_schema_results or None,
                        "user_docs_results": user_docs_results or None,
                        "query_to_run": query_to_run or None,
                        "assistant_response": full_response or None,
                    }
                    st.session_state.query_history.append(interaction)

                    st.rerun()

    @staticmethod
    def init_session_state():
        if "vector_store" not in st.session_state:
            st.session_state.vector_store = None
        if "show_banner" not in st.session_state:
            st.session_state.show_banner = True
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "indexed_files" not in st.session_state:
            st.session_state.indexed_files = set()
        if "uploaded_files_size" not in st.session_state:
            st.session_state.uploaded_files_size = 0
        if "query_history" not in st.session_state:
            st.session_state.query_history = []
        if "current_executed_sql" not in st.session_state:
            st.session_state.current_executed_sql = None
        if "persist_status_for_rerun" not in st.session_state:
            st.session_state.persist_status_for_rerun = False