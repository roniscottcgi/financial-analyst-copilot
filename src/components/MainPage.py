import streamlit as st

from src.components.ChatUI import ChatUI
from src.components.HistoryPage import HistoryPage
from src.components.QueryPage import QueryPage
from src.service.llm_service import LLMService

class MainPage:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def render(self):
        # Create columns (adjust ratios to fit your needs)
        left_sidebar, main_content, right_sidebar = st.columns([2, 4, 2], border=True)

        # Left sidebar
        with left_sidebar:
            left_sidebar_ui = HistoryPage("source for now")
            left_sidebar_ui.render()

        # Main content
        with main_content:
            right_sidebar_ui = QueryPage("source for now")
            right_sidebar_ui.render()

        # Right sidebar
        with right_sidebar:
            right_sidebar_ui = ChatUI(llm_service=self.llm_service)
            right_sidebar_ui.render()