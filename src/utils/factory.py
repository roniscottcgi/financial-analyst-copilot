import streamlit as st
import os
import re
import sqlite3
import httpx as httpx
from sqlalchemy import text

from langchain_community.utilities import SQLDatabase

from langchain_chroma import Chroma
from langchain_core.callbacks.manager import logger
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy import create_engine

DB_FILE = 'db/sample.db'
DB_SCHEMA = 'db/schema.sql'

@st.cache_resource
def init_openai_client():
    try:
        model = st.session_state["openai_model"]
        return ChatOpenAI(
            model=model,
            http_client=httpx.Client(verify=False),
            temperature=0)
    except Exception as e:
        logger.error(e)

def init_db():
    test = os.path.exists(DB_FILE)
    if not test:
        try:
            os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

            connection = sqlite3.connect(DB_FILE, check_same_thread=False)
            cursor = connection.cursor()

            with open(DB_SCHEMA, 'r') as f:
                raw_schema = f.read()

            clean_schema = re.sub(r'(\d{4}-\d{2}-\d{2})\s(\d):', r'\1 0\2:', raw_schema)
            cursor.executescript(clean_schema)
            connection.commit()
            connection.close()
        except Exception as e:
            logger.error(e)
            return None

@st.cache_resource
def get_engine():
    try:
        return create_engine(
            f"sqlite:///{DB_FILE}",
            connect_args={"check_same_thread": False})
    except Exception as e:
        logger.error(e)
        return None

def get_database():
    try:
        engine = get_engine()
        return SQLDatabase(engine, sample_rows_in_table_info=3)
    except Exception as e:
        logger.error(f"Failed to initialize LangChain DB client: {e}")
        return None


def extract_schema_via_sqlite(sql_file_path):
    db_engine = get_engine()
    with db_engine.connect() as conn:
        query = "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"

        rows = conn.execute(text(query)).fetchall()

        return {row[0]: row[1] for row in rows}

@st.cache_resource
def get_embeddings():
    return OpenAIEmbeddings(
        api_key=st.secrets["OPENAI_API_KEY"],
        http_client=httpx.Client(verify=False)
    )

# 2. Cache the actual LangChain Vector Store connection
def get_vector_store(collection_name):
    # This connects to your Docker container via the persistent HTTP Client
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        host="localhost",
        port=8000
    )

@st.cache_resource
def append_to_vector_store(chunks, ids, collection_name):
    if not chunks:
        return None

    # 1. Fetch your cached connection to Docker
    vector_store = get_vector_store(collection_name)

    # 2. Prevent duplication: Query existing records inside Docker
    try:
        existing_data = vector_store.get(ids=ids)
        existing_ids = set(existing_data.get("ids", []))
    except Exception:
        existing_ids = set()

    # 3. Only keep chunks that do not already exist in Docker
    new_chunks = []
    new_ids = []
    for chunk, chunk_id in zip(chunks, ids):
        if chunk_id not in existing_ids:
            new_chunks.append(chunk)
            new_ids.append(chunk_id)

    # 4. Safely write only unique entries to Docker
    if new_chunks:
        vector_store.add_documents(documents=new_chunks, ids=new_ids)
        print(f"Added {len(new_chunks)} new records to {collection_name}.")
    else:
        print(f"All {collection_name} records already exist. Skipping upload.")

    return vector_store


import pandas as pd
from sqlalchemy import create_engine


def run_read_only_query(sql_query: str) -> str:
    """Executes an LLM generated SQL query using read-only credentials."""
    try:
        # Enforce application-level keyword validation
        forbidden_keywords = ["drop", "delete", "insert", "update", "alter", "truncate"]
        if any(kw in sql_query.lower() for kw in forbidden_keywords):
            return "Error: Security violation. Destructive actions are strictly prohibited."

        # Initialize your database connection (Ensure user has ONLY SELECT permissions)
        # Example: engine = create_engine("postgresql://ai_chat_user:password@localhost:5432/mydb")
        engine = get_engine()
            # create_engine("sqlite:///:memory:")  # Replace with your read-only connection

        # Read query directly into a Pandas DataFrame for easy formatting
        df = pd.read_sql_query(sql_query, engine)

        # Automatically cap large outputs to prevent context window bloating
        df_limited = df.head(100)

        return df_limited.to_json(orient="records")
    except Exception as e:
        return f"Database Execution Error: {str(e)}"