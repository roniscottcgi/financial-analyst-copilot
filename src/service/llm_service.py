from langchain_openai import ChatOpenAI

class LLMService:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm_client = llm_client

    def send_request_to_assistant(self, model: str, message: list):
        return self.llm_client.stream(
            message,
            config={"model": model})

