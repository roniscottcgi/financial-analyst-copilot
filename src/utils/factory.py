import streamlit as st
import os
import re
import sqlite3
import httpx as httpx
from langchain_community.utilities import SQLDatabase
from langchain_core.callbacks.manager import logger
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine

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

@st.cache_resource
def init_db():
    DB_FILE = 'db/sample.db'
    DB_SCHEMA = 'db/schema.sql'
    db_exists = os.path.exists(DB_FILE)

    connection = sqlite3.connect(DB_FILE, check_same_thread=False)

    if not db_exists:
        cursor = connection.cursor()
        with open(DB_SCHEMA, 'r') as f:
            raw_schema = f.read()

        clean_schema = re.sub(r'(\d{4}-\d{2}-\d{2})\s(\d):', r'\1 0\2:', raw_schema)

        cursor.executescript(clean_schema)
        connection.commit()

    return connection

@st.cache_resource
def init_database_client():
    try:
        shared_connection = init_db()
        st.session_state.db_connection = shared_connection
        engine = create_engine("sqlite://", creator=lambda: shared_connection)
        return SQLDatabase(engine, sample_rows_in_table_info=3), shared_connection
    except Exception as e:
        logger.error(f"Failed to initialize LangChain DB client: {e}")
        return None