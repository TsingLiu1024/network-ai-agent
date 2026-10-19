from llm.validator import validate_llm_config


def check_startup(config=None):
    valid, _ = validate_llm_config(config)
    return valid
