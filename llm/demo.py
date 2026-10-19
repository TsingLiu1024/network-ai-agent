import json

from .base import BaseLLM


class DemoLLM(BaseLLM):
    """Explicit offline demo; never a real diagnosis."""

    def __init__(self, config=None):
        super().__init__("demo", config)

    def chat(self, prompt, timeout=None):
        self.validate_prompt(prompt)
        if "REPAIR_PLAN" in prompt:
            return json.dumps(
                {
                    "reason": "演示模式：未进行模型诊断",
                    "steps": ["配置模型并获取真实检测证据"],
                    "commands": [],
                },
                ensure_ascii=False,
            )
        return "演示模式：这是离线演示输出，不是真实诊断结论。"
