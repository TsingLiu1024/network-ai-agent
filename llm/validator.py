from config.settings import settings

from .factory import get_llm


def validate_llm_config(config=None):
    try:
        get_llm(config or settings)
        return True, "LLM configuration valid"
    except ValueError:
        return False, "LLM configuration invalid: check provider credentials"
