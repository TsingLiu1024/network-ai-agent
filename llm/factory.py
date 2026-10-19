from config.settings import settings

from .deepseek import DeepSeekLLM
from .demo import DemoLLM
from .ollama import OllamaLLM
from .openai import OpenAILLM


def get_llm(config=None):
    config = config or settings
    return {"ollama": OllamaLLM, "openai": OpenAILLM, "deepseek": DeepSeekLLM, "demo": DemoLLM}[
        config.MODEL_PROVIDER
    ](config)
