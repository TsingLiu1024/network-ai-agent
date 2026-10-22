"""Character budgets are conservative limits, not exact model token counts."""

import re


def redact(text):
    text = re.sub(
        r"(?i)((?:authorization|api[_-]?key|password|token)[\"']?\s*[:=]\s*[\"']?(?:bearer\s+)?)[^\s,;\"'}]+",
        r"\1[REDACTED]",
        text,
    )
    return re.sub(r"sk-[A-Za-z0-9_-]{12,}", "[REDACTED]", text)


def redact_data(value):
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {
            key: "[REDACTED]"
            if str(key).lower().replace("_", "").replace("-", "")
            in {"apikey", "authorization", "password", "token"}
            else redact_data(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    return value


def bounded_prompt(instruction, context, limit):
    if len(instruction) >= limit:
        raise ValueError("Context budget too small for instructions")
    context = redact(context)
    available = limit - len(instruction)
    suffix = "\n[内容已截断]"
    if len(context) > available:
        context = context[: max(0, available - len(suffix))] + suffix[:available]
    return instruction + context


class TokenOptimizer:
    def __init__(self, max_length=4000):
        self.max_length = max_length

    def estimate_tokens(self, text):
        return max(1, len(text)) if text else 0

    def truncate(self, text, max_chars):
        return text[:max_chars]

    def optimize_messages(self, messages):
        remaining = self.max_length
        result = []
        for message in messages:
            content = redact(str(message.get("content", "")))[:remaining]
            result.append({"role": message.get("role", "user"), "content": content})
            remaining -= len(content)
        return result, sum(self.estimate_tokens(m["content"]) for m in result)
