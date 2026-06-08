from typing import Any, LiteralString

import streamlit as st
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit.elements.widgets.chat import ChatInputValue

from utils.factory import append_to_vector_store, get_vector_store_by_collection
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

def index_uploaded_files_to_vector_store(uploaded_files: list[UploadedFile] | UploadedFile):
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

def collect_context_from_vector_store(collection: str, query: str | None | ChatInputValue) -> tuple[
    LiteralString, Any]:
    store = get_vector_store_by_collection(collection)

    results = store.similarity_search_with_score(query, k=3)

    context = "\n".join([doc.page_content for doc, _ in results])
    return context, results

def form_prompt(doc_context: str, schema_context: str) -> str:
    return (
        "You are a helpful Financial Assistant with read-only access to a database schema and user documents.\n\n"
        f"--- AVAILABLE DATABASE SCHEMA MATCHES ---\n{schema_context}\n\n"
        f"--- USER DOCUMENT CONTENT ---\n{doc_context}\n\n"
        "INSTRUCTIONS:\n"
        "1. If answering the user's prompt requires extracting metrics, lists, or aggregates from tables, generate a valid SQL query "
        "and invoke the 'run_database_query' tool.\n"
        "2. Do not write example code or say you lack access. Use your tool to grab data.\n"
        "3. If the document content contains the direct answer, answer from the documents.\n"
        "4. Once tool execution data is returned to you, synthesize a clear response for the user.\n"
        "5. CRITICAL: If the user's request is completely unrelated to finance, business, or the provided data (e.g., asking about the weather, personal advice, or general chit-chat), "
        "DO NOT invoke any tools. Instead, politely inform the user that you are a financial assistant and answer their question using your general knowledge if appropriate, or ask them to return to a financial topic.\n"
        "Ask for additional clarity when needed."
    )
