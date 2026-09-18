from abc import ABC, abstractmethod

from .result import ToolResult



class BaseTool(ABC):


    def __init__(
        self,
        name
    ):

        self.name = name



    @abstractmethod
    def run(
        self,
        *args,
        **kwargs
    ):

        raise NotImplementedError



    def success(
        self,
        data=None,
        message=""
    ):


        return ToolResult(

            tool=self.name,

            success=True,

            data=data,

            message=message

        )



    def failure(
        self,
        error,
        message=""
    ):


        return ToolResult(

            tool=self.name,

            success=False,

            error=error,

            message=message

        )