import subprocess

from .base_tool import BaseTool



class WSLTool(BaseTool):


    def __init__(self):

        super().__init__(
            "wsl"
        )



    def run(
        self,
        action
    ):


        commands = {


            "restart":

            "wsl --shutdown"



        }



        if action not in commands:


            return self.failure(

                error="Unknown action"

            )



        try:


            result = subprocess.run(

                commands[action],

                shell=True,

                capture_output=True,

                text=True

            )



            return self.success(

                data=result.stdout,

                message="WSL操作完成"

            )


        except Exception as e:


            return self.failure(

                error=str(e)

            )