import streamlit as st
import os
import re
import sqlite3
import httpx as httpx
from langchain_community.utilities import SQLDatabase
from langchain_core.callbacks.manager import logger
from langchain_openai import ChatOpenAI
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
        connection = init_db()
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