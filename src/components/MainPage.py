import streamlit as st

from src.components.ChatUI import ChatUI
from src.components.HistoryPage import HistoryPage
from src.components.QueryPage import QueryPage

class MainPage:
    def __init__(self):
        self.llm_service = st.session_state.llm_service
        self.db_service = st.session_state.db_service

    def render(self):
        left_sidebar, main_content, right_sidebar = st.columns([2, 4, 2], border=True)

        with left_sidebar:
            left_sidebar_ui = HistoryPage("source for now")
            left_sidebar_ui.render()

        with main_content:
            main_content_ui = QueryPage(llm_service=self.llm_service, db_service=self.db_service)
            main_content_ui.render()

        with right_sidebar:
            right_sidebar_ui = ChatUI(llm_service=self.llm_service)
            right_sidebar_ui.render()