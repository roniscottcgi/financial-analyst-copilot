import streamlit as st
import httpx as httpx
from openai import OpenAI

@st.cache_resource
def get_openai_client():
    custom_http_client = httpx.Client(verify=False)
    return OpenAI(http_client=custom_http_client)