import streamlit as st

from typing import Any
from docx import Document
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.documents import Document as LCDocument
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from streamlit.elements.widgets.chat import ChatInputValue
from langchain_chroma import Chroma
from src.service.llm_service import LLMService
from src.utils.factory import init_vector_store, init_openai_client
from docx import Document
from pypdf import PdfReader


class ChatUI:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def collect_assistant_response(self, message: list[dict[str, Any]]):
        return self.llm_service.send_request_to_assistant(
            model=st.session_state["openai_model"],
            message=message)

    @staticmethod
    def extract_text(uploaded_file):
        name = uploaded_file.name
        if name.endswith('.pdf'):
            pdf_reader = PdfReader(uploaded_file)
            return "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        elif name.endswith('.docx'):
            doc = Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs])
        return ""

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

        if "show_banner" not in st.session_state:
            st.session_state.show_banner = True
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "vector_store" not in st.session_state:
            st.session_state.vector_store = None

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
        uploaded_files = st.file_uploader(
            "Upload your data file(s)",
            type=["docx", "pdf"],
            accept_multiple_files=True)

        if uploaded_files and st.session_state.vector_store is None:
            all_lc_docs = []

            for uploaded_file in uploaded_files:
                text = self.extract_text(uploaded_file)
                if text.strip():
                    doc = LCDocument(page_content=text, metadata={"source": uploaded_file.name})
                    all_lc_docs.append(doc)
                if all_lc_docs:
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    chunks = text_splitter.split_documents(all_lc_docs)

                    with st.spinner("Generating embeddings..."):
                        st.session_state.vector_store = init_vector_store(chunks)
                        st.success(f"Successfully indexed {len(chunks)} text chunks into Chroma!")
                        st.rerun()

        if st.session_state.vector_store is not None:
            # st.caption(":green[✔ Vector Database Status: Active & Loaded]")
            st.markdown(
                '<p style="color: #2ea44f; font-size: 0.85rem; margin: 0;">'
                '<span style="font-size: 1.5rem; vertical-align: middle; padding-right: 4px;">✔</span> '
                'Vector Database Status: Active & Loaded'
                '</p>',
                unsafe_allow_html=True)

        assistant_payload = None

        if new_user_input:
            self.append_chat_messages("user", new_user_input)
            assistant_payload = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

        with chat_container:
            if st.session_state.show_banner and not st.session_state.vector_store:
                with st.container():
                    # Use columns to position an "Exit" or "X" button on the right
                    col1, col2 = st.columns([2, .5])
                    with col1:
                        st.info("💡Upload documents below for RAG-based results.")
                    with col2:
                        # When clicked, this button triggers a rerun and hides the banner
                        if st.button("✖️", key="exit_banner"):
                            st.session_state.show_banner = False
                            st.rerun()
            self.display_chat_history()

            if assistant_payload:
                with st.chat_message("assistant"):
                    # Fallback if user types without uploading docs
                    if st.session_state.vector_store is None:
                        stream = self.collect_assistant_response(assistant_payload)
                        response = st.write_stream(stream)
                        self.append_chat_messages("assistant", response)
                    else:
                        llm_client = init_openai_client()
                        retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 3})

                        system_prompt = (
                            "You are a helpful assistant. Answer the question using only "
                            "the provided context below. If you do not know, say you don't know.\n\n"
                            "Context:\n{context}"
                        )
                        prompt = ChatPromptTemplate.from_messages([
                            ("system", system_prompt),
                            ("human", "{input}"),
                        ])

                        qa_chain = create_stuff_documents_chain(llm_client, prompt)
                        rag_chain = create_retrieval_chain(retriever, qa_chain)

                        placeholder = st.empty()
                        full_response = ""

                        # Smooth streaming block fix
                        for chunk in rag_chain.stream({"input": new_user_input}):
                            if "answer" in chunk:
                                full_response += chunk["answer"]
                                placeholder.markdown(full_response)

                        self.append_chat_messages("assistant", full_response)