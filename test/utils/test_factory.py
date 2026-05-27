import unittest
from unittest.mock import patch, MagicMock

from src.utils.factory import get_openai_client

class TestFactory():

    @patch('src.utils.factory.OpenAI')
    def test_get_openai_client(self, mock_openai_cls):
        mock_instance = MagicMock()
        mock_openai_cls.return_value = mock_instance

        mock_instance.chat.completions.create.return_value = MagicMock()

        # from src.utils.factory import get_openai_client
        result = get_openai_client()

        mock_openai_cls.assert_called_once()
        assert result == mock_instance