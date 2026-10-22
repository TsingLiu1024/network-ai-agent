import json

from agents.repair_agent import RepairAgent
from config.settings import Settings
from llm.optimizer import TokenOptimizer


def test_repair_prompt_redacts_credentials_and_marks_truncation():
    class Model:
        prompt = ""

        def chat(self, prompt, timeout=None):
            self.prompt = prompt
            return json.dumps({"reason": "Unknown", "steps": ["Collect evidence"], "commands": []})

    model = Model()
    result = RepairAgent(Settings(_env_file=None, MAX_CONTEXT_LENGTH=1000), llm=model).run(
        "api_key=confidential\n" + "x" * 3000
    )
    assert result.success
    assert "confidential" not in model.prompt
    assert "[内容已截断]" in model.prompt
    assert len(model.prompt) <= 1000


def test_optimizer_bounds_combined_messages():
    messages, _ = TokenOptimizer(10).optimize_messages(
        [{"role": "user", "content": "a" * 8}, {"role": "user", "content": "b" * 8}]
    )
    assert sum(len(m["content"]) for m in messages) <= 10


def test_json_credentials_are_redacted():
    from llm.optimizer import redact

    result = redact('{"api_key": "confidential", "Authorization": "Bearer private"}')
    assert "confidential" not in result
    assert "private" not in result
