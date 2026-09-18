import os

from .demo import DemoLLM
from .ollama import OllamaLLM
from .openai import OpenAILLM
from .deepseek import DeepSeekLLM



def get_llm():

    provider = os.getenv(
        "LLM_PROVIDER",
        "ollama"
    ).lower()


    if provider == "ollama":

        return OllamaLLM()


    if provider == "openai":

        return OpenAILLM()


    if provider == "deepseek":

        return DeepSeekLLM()


    if provider == "demo":

        return DemoLLM()


    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )