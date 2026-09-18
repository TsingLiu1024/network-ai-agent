import socket

import subprocess


from .base_tool import BaseTool




class NetworkTool(
    BaseTool
):


    def __init__(self):

        super().__init__(
            "network"
        )



    def run(
        self,
        target="8.8.8.8"
    ):


        result = {}



        # ping


        try:


            ping = subprocess.run(

                [
                    "ping",
                    "-n",
                    "4",
                    target
                ],


                capture_output=True,

                text=True

            )


            result["ping"] = (
                ping.stdout
            )


        except Exception as e:


            result["ping_error"] = str(e)




        # DNS


        try:


            ip = socket.gethostbyname(

                "github.com"

            )


            result["dns"] = ip



        except Exception:


            result["dns"] = (
                "DNS Failed"
            )



        return result