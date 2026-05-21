import streamlit as st
import httpx as httpx
from openai import OpenAI

from src.components.MainPage import MainPage
from src.service.llm_service import LLMService

# Expand the page to full width
st.set_page_config(layout="wide")

# Initialize the model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

@st.cache_resource
def get_openai_client():
    # Create custom httpx client with SSL verification turned off
    custom_http_client = httpx.Client(verify=False)
    # Automatically pulls OPENAI_API_KEY from st.secrets or environment
    return OpenAI(http_client=custom_http_client)

# Instantiate Core Logic
client = get_openai_client()
llm_service = LLMService(client=client)

ui = MainPage(llm_service)
ui.render()