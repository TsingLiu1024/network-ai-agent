from config.settings import settings


SUPPORTED_PROVIDERS = {
    "ollama",
    "deepseek",
    "openai",
}


def validate_llm_config():
    """
    检查当前 LLM Provider 的配置是否完整。

    返回：
        (True, "配置正常")
        (False, "错误信息")
    """

    provider = settings.MODEL_PROVIDER.lower().strip()

    if provider not in SUPPORTED_PROVIDERS:
        return (
            False,
            f"不支持的 LLM Provider: {provider}。"
            f"支持：{', '.join(sorted(SUPPORTED_PROVIDERS))}"
        )

    if provider == "ollama":
        if not settings.OLLAMA_URL:
            return False, "OLLAMA_URL 未配置"

        if not settings.OLLAMA_MODEL:
            return False, "OLLAMA_MODEL 未配置"

    elif provider == "deepseek":
        if not settings.DEEPSEEK_API_KEY:
            return False, (
                "DEEPSEEK_API_KEY 未配置。"
                "请在 .env 中设置 DeepSeek API Key。"
            )

        if not settings.DEEPSEEK_MODEL:
            return False, "DEEPSEEK_MODEL 未配置"

    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            return False, (
                "OPENAI_API_KEY 未配置。"
                "请在 .env 中设置 OpenAI API Key。"
            )

        if not settings.OPENAI_MODEL:
            return False, "OPENAI_MODEL 未配置"

    return True, "LLM 配置正常"