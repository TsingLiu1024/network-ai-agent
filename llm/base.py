"""Model failures never masquerade as diagnostic text."""

import json
import time
from abc import ABC, abstractmethod

import requests

from config.settings import settings


class LLMError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class BaseLLM(ABC):
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or settings

    @abstractmethod
    def chat(self, prompt, timeout=None):
        raise NotImplementedError

    def request(self, url, payload, headers=None, timeout=None):
        budget = min(
            self.config.LLM_TIMEOUT, timeout if timeout is not None else self.config.LLM_TIMEOUT
        )
        if budget <= 0:
            raise LLMError("deadline", "Inference deadline exceeded")
        started = time.monotonic()
        response = None
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers or {},
                timeout=budget,
                stream=True,
                allow_redirects=False,
            )
            if not 200 <= response.status_code < 300:
                raise LLMError(
                    "provider_http", f"{self.name} request failed (HTTP {response.status_code})"
                )
            chunks, size = [], 0
            max_bytes = self.config.MAX_LLM_OUTPUT_CHARS * 8 + 16000
            for chunk in response.iter_content(chunk_size=1024):
                if time.monotonic() - started > budget:
                    raise LLMError("deadline", "Inference deadline exceeded")
                size += len(chunk)
                if size > max_bytes:
                    raise LLMError("output_limit", "Model response exceeds byte limit")
                chunks.append(chunk)
            data = json.loads(b"".join(chunks))
        except (requests.RequestException, ValueError) as exc:
            raise LLMError("provider_unavailable", f"{self.name} request failed") from exc
        finally:
            if response is not None:
                response.close()
        if time.monotonic() - started > budget:
            raise LLMError("deadline", "Inference deadline exceeded")
        if not isinstance(data, dict):
            raise LLMError("invalid_response", "Invalid model response")
        return data

    def validate_prompt(self, prompt):
        if not isinstance(prompt, str) or not prompt.strip():
            raise LLMError("invalid_prompt", "Prompt cannot be empty")
        if len(prompt) > self.config.MAX_CONTEXT_LENGTH:
            raise LLMError("context_limit", "Prompt exceeds context budget")

    def content(self, value):
        if not isinstance(value, str) or not value.strip():
            raise LLMError("invalid_response", "Model returned no text")
        if len(value) > self.config.MAX_LLM_OUTPUT_CHARS:
            raise LLMError("output_limit", "Model output exceeds limit")
        return value.strip()
