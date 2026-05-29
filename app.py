import streamlit as st

from src.components.MainPage import MainPage
from src.service import db_service
from src.service.db_service import DBService
from src.utils.factory import init_openai_client, init_database_client, init_db
from src.service.llm_service import LLMService

st.set_page_config(layout="wide")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "llm_service" not in st.session_state:
    llm_client = init_openai_client()
    if llm_client is None:
        st.error("Failed to initialize openai client.")
        st.stop()
    st.session_state.llm_client = llm_client
    llm_service = LLMService(llm_client=st.session_state.llm_client)
    if llm_service is None:
        st.error("Failed to initialize openai client.")
        st.stop()
    st.session_state.llm_service = llm_service

if "db_service" not in st.session_state:
    db_client, db_connection = init_database_client()
    if db_client is None:
        st.error("Failed to initialize database.")
        st.stop()
    st.session_state.db_client = db_client
    if db_connection is None:
        st.error("Failed to initialize database.")
        st.stop()
    st.session_state.db_connection = db_connection
    db_service = DBService(db_client=st.session_state.db_client)
    if db_service is None:
        st.error("Failed to initialize database.")
        st.stop()
    st.session_state.db_service = db_service

st.session_state.db_service.create_db_chain(
    llm_client=st.session_state.llm_client,
    db_client=st.session_state.db_client)

ui = MainPage()
ui.render()