import os
import requests


from .base import BaseLLM



class OpenAILLM(BaseLLM):


    def __init__(self):

        super().__init__(
            name="openai"
        )


        self.key=os.getenv(
            "OPENAI_API_KEY"
        )


    def chat(
        self,
        prompt:str
    ):


        if not self.key:

            return "OpenAI API key missing"



        response=requests.post(

            "https://api.openai.com/v1/chat/completions",

            headers={

                "Authorization":
                f"Bearer {self.key}",

                "Content-Type":
                "application/json"

            },

            json={

                "model":
                "gpt-4o-mini",

                "messages":[

                    {
                        "role":"user",
                        "content":prompt
                    }

                ]

            }

        )


        return (
            response.json()
            ["choices"][0]
            ["message"]
            ["content"]
        )