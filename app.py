import streamlit as st

from src.components.MainPage import MainPage
from src.utils.factory import get_openai_client
from src.service.llm_service import LLMService

st.set_page_config(layout="wide")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

client = get_openai_client()
llm_service = LLMService(client=client)

ui = MainPage(llm_service)
ui.render()