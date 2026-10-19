from .base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, config=None):
        super().__init__("ollama", config)
        self.host = self.config.OLLAMA_URL
        self.model = self.config.OLLAMA_MODEL

    def chat(self, prompt, timeout=None):
        self.validate_prompt(prompt)
        data = self.request(
            f"{self.host}/api/generate",
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 2048},
            },
            timeout=timeout,
        )
        return self.content(data.get("response"))
