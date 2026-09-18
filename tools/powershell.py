import subprocess

from .base_tool import BaseTool

from .policy import ToolPolicy



class PowerShellTool(BaseTool):


    def __init__(self):

        super().__init__(
            "powershell"
        )



    def run(
        self,
        command
    ):


        if not ToolPolicy.check(
            command
        ):


            return self.failure(

                error="Command blocked",

                message="危险命令被安全策略阻止"

            )



        try:


            result = subprocess.run(

                [

                    "powershell",

                    "-Command",

                    command

                ],


                capture_output=True,


                text=True,


                timeout=30

            )


            return self.success(

                data={

                    "stdout":
                    result.stdout,


                    "stderr":
                    result.stderr,


                    "returncode":
                    result.returncode

                },

                message="PowerShell执行完成"

            )


        except Exception as e:


            return self.failure(

                error=str(e),

                message="PowerShell执行失败"

            )