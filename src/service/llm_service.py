from openai import OpenAI

class LLMService:
    def __init__(self, client: ChatOpenAI):
        self.client = client

    def send_request_to_assistant(self, model: str, message: list):
        return self.client.stream(
            message,
            config={"model": model})

