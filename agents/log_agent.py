"""
Log Analysis Agent

负责:
- Windows日志采集
- 日志异常分析
- LLM辅助诊断
"""


import subprocess


from agents.core.base_agent import BaseAgent
from agents.core.result import AgentResult

from llm import get_llm





class LogAgent(BaseAgent):


    def __init__(self):


        super().__init__(

            name="log_agent",

            description="Windows log analysis agent"

        )


        self.llm = get_llm()





    def collect_logs(
        self
    ):


        """
        获取Windows事件日志
        """


        try:


            result = subprocess.run(

                [
                    "powershell",

                    "-Command",

                    """
                    Get-WinEvent 
                    -LogName System 
                    -MaxEvents 30 |
                    Select TimeCreated,
                    LevelDisplayName,
                    ProviderName,
                    Id,
                    Message |
                    Format-Table -AutoSize
                    """

                ],


                capture_output=True,

                text=True,

                encoding="utf-8",

                errors="ignore",

                timeout=20

            )



            return result.stdout



        except Exception as e:


            return str(e)







    def run(
        self,
        query:str
    ) -> AgentResult:



        try:


            logs = self.collect_logs()



            prompt=f"""

你是Windows系统故障分析专家。


用户问题:

{query}



下面是Windows系统日志:

{logs}



请分析:

1. 是否存在相关异常

2. 关键错误事件

3. 可能原因

4. 修复建议


请使用中文回答。

"""



            analysis = self.llm.chat(

                prompt

            )




            return AgentResult(

                agent=self.name,

                success=True,

                data={

                    "logs":logs,

                    "analysis":analysis

                },

                message="日志分析完成"

            )





        except Exception as e:



            return AgentResult(

                agent=self.name,

                success=False,

                data={},

                message=str(e)

            )