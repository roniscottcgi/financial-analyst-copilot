from unittest.mock import patch
from streamlit.testing.v1 import AppTest

@patch('src.service.llm_service.LLMService')
class TestChatUI:

    def _run_chat_app(self, llm_service_mock) -> AppTest:
        llm_service_mock_instance = llm_service_mock.return_value

        def run_app(llm_mock):
            from src.components.ChatUI import ChatUI
            page = ChatUI(llm_service=llm_mock)
            page.render()

        return AppTest.from_function(run_app, args=(llm_service_mock_instance,)).run()

    def test_chat_ui(self, llm_service_mock):
        at = self._run_chat_app(llm_service_mock)

        assert at
        assert at.title[0].value == "Financial Assistant Chat"
        assert len(at.columns) == 2

    def test_chat_ui_with_toggle_off(self, llm_service_mock):
        at = self._run_chat_app(llm_service_mock)

        assert at.toggle(key="sidebar_toggle").label == "Show Chat Assistant"
        assert at.toggle(key="sidebar_toggle").value == False

        assert len(at.info) == 1
        assert at.info[0].value == "Chat is currently closed. Toggle the chat window to open the chat assistant."
        assert len(at.chat_input) == 0

    def test_chat_ui_with_toggle_on(self, llm_service_mock):
        at = self._run_chat_app(llm_service_mock)

        assert at
        at.toggle(key="sidebar_toggle").set_value(True).run()

        assert at.toggle(key="sidebar_toggle").value == True
        assert at.chat_input[0].placeholder == "How can I assist you?"

    def test_chat_ui_conversation(self, llm_service_mock):
        at = self._run_chat_app(llm_service_mock)

        assert at
        at.toggle(key="sidebar_toggle").set_value(True).run()

        at.chat_input(key="chat_input_key").set_value("Test").run()

        assert len(at.session_state.messages) == 1
        assert at.session_state.messages[0]['role'] == "user"
        assert at.session_state.messages[0]['content'] == "Test"


