import streamlit as st

from src.components.ChatUI import ChatUI
from src.components.HistoryPage import HistoryPage
from src.components.QueryPage import QueryPage
from src.service.db_service import DBService
from src.service.llm_service import LLMService


class MainPage:
    def __init__(self, llm_service: LLMService, db_service: DBService):
        self.llm_service = llm_service
        self.db_service = db_service

    def render(self):
        left_sidebar, main_content, right_sidebar = st.columns([3, 4, 3], border=True)

        with left_sidebar:
            left_sidebar_ui = HistoryPage("source for now")
            left_sidebar_ui.render()

        with main_content:
            right_sidebar_ui = ChatUI(llm_service=self.llm_service)
            right_sidebar_ui.render()

        with right_sidebar:
            main_content_ui = QueryPage(llm_service=self.llm_service, db_service=self.db_service)
            main_content_ui.render()