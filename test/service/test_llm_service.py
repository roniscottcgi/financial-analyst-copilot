from unittest.mock import patch, MagicMock

from src.service.llm_service import LLMService


class TestLLMService():

    @patch('openai.OpenAI')
    def test_send_request_to_assistant(self, open_ai_mock):
        mock_response_chunk_1 = MagicMock()
        mock_response_chunk_1.choices = [MagicMock(delta=MagicMock(content="hello "))]

        mock_response_chunk_2 = MagicMock()
        mock_response_chunk_2.choices = [MagicMock(delta=MagicMock(content="there!"))]

        open_ai_mock_instance = open_ai_mock.return_value
        mock_create = open_ai_mock_instance.chat.completions.create

        mock_create.return_value = [mock_response_chunk_1, mock_response_chunk_2]

        service = LLMService(llm_client=open_ai_mock_instance)

        stream_response = service.send_request_to_assistant(
            model="test-model",
            message=[{'role': 'user', 'content': 'hey'}])

        mock_create.assert_called_once_with(
            model="test-model",
            messages=[{'role': 'user', 'content': 'hey'}],
            stream=True)

        collected_text = ""
        for chunk in stream_response:
            collected_text += chunk.choices[0].delta.content

        assert collected_text == "hello there!"



