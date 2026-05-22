import unittest
from unittest.mock import patch, MagicMock

class TestFactory(unittest.TestCase):

    @patch('src.utils.factory.OpenAI')
    def test_get_openai_client(self, mock_openai_cls):
        # 1. Setup the mock instance to return fake completions or objects
        mock_instance = MagicMock()
        mock_openai_cls.return_value = mock_instance

        # 2. Configure the simulated API response
        mock_instance.chat.completions.create.return_value = MagicMock()

        # 3. Call your function/method that instantiates OpenAI
        from src.utils.factory import get_openai_client
        result = get_openai_client()

        # 4. Verify the client was instantiated and called
        mock_openai_cls.assert_called_once()
        assert result == mock_instance