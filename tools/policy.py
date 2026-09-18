class ToolPolicy:


    """
    工具执行策略。

    防止危险命令直接执行。
    """


    BLOCKED_COMMANDS = [

        "rm -rf",

        "format",

        "del /f",

        "shutdown",

        "reboot"

    ]



    @classmethod
    def check(
        cls,
        command
    ):


        command = command.lower()



        for blocked in cls.BLOCKED_COMMANDS:


            if blocked in command:


                return False



        return True