from llm.validator import validate_llm_config
from config.settings import settings


def check_startup():
    """
    执行项目启动前的基础检查。
    """

    print("=" * 60)
    print("Network AI Agent - Startup Check")
    print("=" * 60)

    print(f"LLM Provider : {settings.MODEL_PROVIDER}")
    print(f"RAG          : Enabled")
    print(
        f"Token Optimizer : "
        f"{'Enabled' if settings.ENABLE_TOKEN_OPTIMIZER else 'Disabled'}"
    )
    print()

    # LLM 配置检查
    valid, message = validate_llm_config()

    if valid:
        print(f"[OK] {message}")
    else:
        print(f"[ERROR] {message}")
        print("=" * 60)
        return False

    print()
    print("[OK] Startup check passed")
    print("=" * 60)

    return True