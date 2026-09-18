import os
import requests

from .base import BaseLLM



class OllamaLLM(BaseLLM):


    def __init__(self):

        super().__init__(
            name="ollama"
        )


        self.host = os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434"
        )


        self.model = os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5"
        )



    def chat(
        self,
        prompt: str
    ) -> str:


        try:

            response = requests.post(

                f"{self.host}/api/generate",

                json={

                    "model": self.model,

                    "prompt": prompt,

                    "stream": False

                },

                timeout=60

            )


            data = response.json()


            return data.get(
                "response",
                ""
            )


        except Exception as e:

            return f"Ollama error: {e}"