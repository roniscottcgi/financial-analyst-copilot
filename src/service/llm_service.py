from typing import List

from openai import OpenAI

class LLMService:
    def __init__(self, client: OpenAI):
        self.client = client  # Store the client instance

    def get_chat_stream(self, model: str, message: list):
        # Service handles raw OpenAI call internally
        return self.client.chat.completions.create(
            model=model,
            messages=message,
            stream=True
        )

