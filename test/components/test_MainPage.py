from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class TestMainPage:

    @patch("src.components.HistoryPage.HistoryPage")
    @patch("src.components.QueryPage.QueryPage")
    @patch("src.components.ChatUI.ChatUI")
    @patch("src.service.llm_service.LLMService")
    def test_main_page(
        self, llm_service_mock, chat_ui_mock, query_page_mock, history_page_mock
    ):
        mock_llm_instance = llm_service_mock.return_value
        mock_chat_ui_instance = chat_ui_mock.return_value
        mock_query_page_instance = query_page_mock.return_value
        mock_history_page_instance = history_page_mock.return_value

        def run_app(llm_mock):
            from src.components.MainPage import MainPage

            page = MainPage(llm_service=llm_mock)
            page.render()

        at = AppTest.from_function(run_app, args=(mock_llm_instance,)).run()

        assert not at.exception

        history_page_mock.assert_called_once()
        mock_history_page_instance.render.assert_called_once()

        query_page_mock.assert_called_once()
        mock_query_page_instance.render.assert_called_once()

        chat_ui_mock.assert_called_once()
        mock_chat_ui_instance.render.assert_called_once()