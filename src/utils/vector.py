from typing import Any, LiteralString

import streamlit as st
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit.elements.widgets.chat import ChatInputValue

from utils.factory import append_to_vector_store, get_vector_store
from langchain_core.messages import SystemMessage
from docx import Document
from pypdf import PdfReader

def extract_text(uploaded_file):
    name = uploaded_file.name
    if name.endswith('.pdf'):
        pdf_reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif name.endswith('.docx'):
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

def index_uploaded_files(uploaded_files: list[UploadedFile] | UploadedFile):
    all_lc_docs = []
    chunks = []
    stable_ids = []

    for i, uploaded_file in enumerate(uploaded_files):
        if uploaded_file.name in st.session_state.indexed_files:
            continue

        text = extract_text(uploaded_file)
        if text.strip():
            doc = LCDocument(page_content=text, metadata={"source": uploaded_file.name})
            all_lc_docs.append(doc)
        if all_lc_docs:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""])
            chunks = text_splitter.split_documents(all_lc_docs)
            doc_id = f"{i}:{uploaded_file.name}"
            stable_ids.append(doc_id)
        st.session_state.indexed_files.add(uploaded_file.name)

        vector_store = append_to_vector_store(
            chunks=chunks,
            ids=stable_ids,
            collection_name="user_documents")
        return vector_store, chunks

def collect_context( new_user_input: str | None | ChatInputValue) -> tuple[LiteralString, LiteralString, Any, Any]:
    user_docs_store = get_vector_store("user_documents")
    db_schema_store = get_vector_store("db_schema")

    user_docs_results = user_docs_store.similarity_search_with_score(new_user_input, k=3)
    db_schema_results = db_schema_store.similarity_search_with_score(new_user_input, k=4)

    schema_context = "\n".join([doc.page_content for doc, _ in db_schema_results])
    doc_context = "\n".join([doc.page_content for doc, _ in user_docs_results])
    return doc_context, schema_context, user_docs_results, db_schema_results

def append_langchain_messages(doc_context: str, new_user_input: str | None | ChatInputValue, schema_context: str) -> list[SystemMessage]:
    system_prompt = (
        "You are a helpful Financial Assistant with read-only access to a database schema and user documents.\n\n"
        f"--- AVAILABLE DATABASE SCHEMA MATCHES ---\n{schema_context}\n\n"
        f"--- USER DOCUMENT CONTENT ---\n{doc_context}\n\n"
        "INSTRUCTIONS:\n"
        "1. If answering the user's prompt requires extracting metrics, lists, or aggregates from tables, generate a valid SQL query "
        "and invoke the 'run_database_query' tool.\n"
        "2. Do not write example code or say you lack access. Use your tool to grab data.\n"
        "3. If the document content contains the direct answer, answer from the documents.\n"
        "4. Once tool execution data is returned to you, synthesize a clear response for the user."
    )

    # Re-map chat history to official LangChain message classes
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

    langchain_messages = [SystemMessage(content=system_prompt)]
    for m in st.session_state.messages[:-1]:  # Append previous conversational history
        if m["role"] == "user":
            langchain_messages.append(HumanMessage(content=m["content"]))
        else:
            langchain_messages.append(AIMessage(content=m["content"]))
    # Add current user prompt
    langchain_messages.append(HumanMessage(content=new_user_input))
    return langchain_messages
