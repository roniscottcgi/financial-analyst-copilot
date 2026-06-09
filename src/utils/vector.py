import io

import docx
import fitz
import pymupdf4llm
import streamlit as st
from typing import Any, LiteralString

from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit.elements.widgets.chat import ChatInputValue
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from utils.factory import append_to_vector_store, get_vector_store_by_collection

def extract_text(uploaded_file):
    """
    100% offline document to markdown parser using pymupdf4llm and python-docx.
    """
    try:
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        # --- Handle PDF files ---
        if uploaded_file.name.lower().endswith('.pdf'):
            # Open the file bytes via fitz first to handle in-memory buffer safely
            doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")

            # Pass the parsed fitz document into the markdown converter
            markdown_text = pymupdf4llm.to_markdown(doc)
            return markdown_text

        # --- Handle DOCX files ---
        elif uploaded_file.name.lower().endswith('.docx'):
            doc = docx.Document(io.BytesIO(file_bytes))
            md_lines = []
            for paragraph in doc.paragraphs:
                style = paragraph.style.name
                if style.startswith('Heading 1'):
                    md_lines.append(f"# {paragraph.text}")
                elif style.startswith('Heading 2'):
                    md_lines.append(f"## {paragraph.text}")
                elif style.startswith('Heading 3'):
                    md_lines.append(f"### {paragraph.text}")
                else:
                    md_lines.append(paragraph.text)
            return "\n\n".join(md_lines)

        else:
            st.error(f"Unsupported file format: {uploaded_file.name}")
            return ""

    except Exception as e:
        st.error(f"Failed to parse {uploaded_file.name}: {e}")
        return ""

def index_uploaded_files_to_vector_store(uploaded_files: list[UploadedFile] | UploadedFile):
    if not isinstance(uploaded_files, list):
        uploaded_files = [uploaded_files]

    all_chunks = []
    all_stable_ids = []

    # Identify structural headings extracted from the PDF/DOCX
    headers_to_split_on = [
        ("#", "Header_1"),
        ("##", "Header_2"),
        ("###", "Header_3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    # Sub-split oversized sections so they comfortably fit your vector tokens
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    for i, uploaded_file in enumerate(uploaded_files):
        if uploaded_file.name in st.session_state.indexed_files:
            continue

        # Extract text into Markdown string format
        text = extract_text(uploaded_file)
        if not text.strip():
            continue

        # Split structurally by the headings extracted from your PDF/DOCX
        sections = markdown_splitter.split_text(text)

        # Guard rail: ensure giant document sections are safely divided
        file_chunks = text_splitter.split_documents(sections)

        # Inject original file name metadata back into the final chunks
        for chunk in file_chunks:
            chunk.metadata["source"] = uploaded_file.name

        # Create stable chunk IDs
        for chunk_idx, chunk in enumerate(file_chunks):
            chunk_id = f"{uploaded_file.name}_{i}_{chunk_idx}"
            all_stable_ids.append(chunk_id)
            all_chunks.append(chunk)

        st.session_state.indexed_files.add(uploaded_file.name)

    if all_chunks:
        vector_store = append_to_vector_store(
            chunks=all_chunks,
            ids=all_stable_ids,
            collection_name="user_documents"
        )
        return vector_store, all_chunks

    return None, []


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
