import streamlit as st

from src.components.MainPage import MainPage
from src.service import db_service
from src.service.db_service import DBService
from src.utils.factory import get_openai_client, get_database, init_db
from src.utils.ingest import build_and_load_vector
from src.service.llm_service import LLMService

st.set_page_config(layout="wide")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "vector_store" not in st.session_state:
    st.session_state["vector_store"] = None

llm_client = get_openai_client()
if llm_client is None:
    st.error("Failed to initialize openai client.")
    st.stop()
st.session_state.llm_client = llm_client
llm_service = LLMService(llm_client=llm_client)
if llm_service is None:
    st.error("Failed to initialize openai client.")
    st.stop()

db_client = get_database()
if db_client is None:
    st.error("Failed to initialize database.")
    st.stop()
db_service = DBService(db_client=db_client)
if db_service is None:
    st.error("Failed to initialize database.")
    st.stop()

build_and_load_vector()

ui = MainPage(llm_service=llm_service,
              db_service=db_service)
ui.render()