import streamlit as st
import httpx as httpx
from langchain_community.utilities import SQLDatabase
from langchain_core.callbacks.manager import logger
from langchain_openai import ChatOpenAI
from openai import OpenAI

@st.cache_resource
def init_openai_client():
    try:
        model = st.session_state["openai_model"]
        return ChatOpenAI(
            model=model,
            http_client=httpx.Client(verify=False))
    except Exception as e:
        logger.error(e)

@st.cache_resource
def init_database_client():
    try:
        db_uri = "sqlite:///sample.db"
        return SQLDatabase.from_uri(db_uri)
    except Exception as e:
        logger.error(e)
