import streamlit as st

from src.components.MainPage import MainPage
from src.service.db_service import DBService
from src.utils.factory import init_openai_client, init_database_client
from src.service.llm_service import LLMService

st.set_page_config(layout="wide")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "llm_service" not in st.session_state:
    llm_client = init_openai_client()
    st.session_state.llm_service = LLMService(llm_client)

if "db_service" not in st.session_state:
    db_client = init_database_client()
    db_service = DBService(client=db_client)
    db_service.create_db_chain(llm_client=llm_client, db_client=db_client)
    st.session_state.db_service = db_service

ui = MainPage()
ui.render()