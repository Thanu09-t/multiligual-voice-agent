from app.providers.llm.openai import OpenAILLMProvider


class GroqLLMProvider(OpenAILLMProvider):
    """Groq Cloud API provider using ultra-low latency models."""

    def __init__(self, api_key: str, model: str = "qwen/qwen3.8-27b"):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://api.groq.com/openai/v1",
        )
