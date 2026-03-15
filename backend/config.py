import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "anthropic")
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            # model = "claude-haiku-4-5",
            model="claude-haiku-4-5-20251001",
            temperature=0.7,
            max_tokens=4096,
        )
    # TODO: elif provider == "ollama":
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")