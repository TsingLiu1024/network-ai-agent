from abc import ABC, abstractmethod



class BaseLLM(ABC):


    def __init__(
        self,
        name:str
    ):

        self.name=name



    @abstractmethod
    def chat(
        self,
        prompt:str
    ):
        pass