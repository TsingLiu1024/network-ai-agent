import os
import requests


from .base import BaseLLM



class DeepSeekLLM(BaseLLM):


    def __init__(self):

        super().__init__(
            name="deepseek"
        )


        self.api_key = os.getenv(
            "DEEPSEEK_API_KEY"
        )


        self.url = (
            "https://api.deepseek.com/chat/completions"
        )



    def chat(
        self,
        prompt:str
    ):


        if not self.api_key:

            return (
                "DeepSeek API key missing"
            )


        try:


            response = requests.post(

                self.url,

                headers={

                    "Authorization":
                    f"Bearer {self.api_key}",

                    "Content-Type":
                    "application/json"

                },

                json={

                    "model":
                    "deepseek-chat",

                    "messages":[

                        {
                            "role":"user",
                            "content":prompt
                        }

                    ]

                },

                timeout=60

            )


            data=response.json()


            if "choices" not in data:
                return f"DeepSeek error: {data}"

            return (
                data["choices"][0]
                ["message"]
                ["content"]
            )


        except Exception as e:

            return str(e)