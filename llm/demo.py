from .base import BaseLLM



class DemoLLM(BaseLLM):


    def __init__(self):

        super().__init__(
            name="demo"
        )



    def chat(
        self,
        prompt: str
    ) -> str:


        return {
            "status": "demo",
            "message": "Demo mode response",
            "prompt": prompt
        }