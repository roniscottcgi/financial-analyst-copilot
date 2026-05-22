import streamlit as st
import httpx as httpx
from openai import OpenAI

@st.cache_resource
def get_openai_client():
    # Create custom httpx client with SSL verification turned off
    custom_http_client = httpx.Client(verify=False)
    # Automatically pulls OPENAI_API_KEY from st.secrets or environment
    return OpenAI(http_client=custom_http_client)