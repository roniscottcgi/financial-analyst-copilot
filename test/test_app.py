import unittest
from unittest.mock import patch, Mock, MagicMock

from streamlit.testing.v1 import AppTest

class TestApp(unittest.TestCase):

    @patch('src.utils.factory.get_openai_client')
    @patch('src.service.llm_service.LLMService')
    @patch('src.components.MainPage.MainPage')
    def test_app(self, main_page_mock, llm_service_mock, openai_client_mock):
        mock_client_instance = openai_client_mock.return_value
        mock_llm_instance = llm_service_mock.return_value
        mock_ui_instance = main_page_mock.return_value

        # Run the app
        at = AppTest.from_file("app.py").run()

        # Verify the render method on that specific instance was called
        mock_client_instance.return_value = mock_client_instance
        mock_llm_instance.return_value = mock_llm_instance
        mock_ui_instance.render.assert_called_once()