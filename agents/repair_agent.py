"""
Repair Agent

负责:
- 根据诊断结果生成修复方案
- 生成可执行命令
"""


from agents.core.base_agent import BaseAgent
from agents.core.result import AgentResult

from llm import get_llm





class RepairAgent(BaseAgent):


    def __init__(self):


        super().__init__(

            name="repair_agent",

            description="Network repair suggestion agent"

        )


        self.llm = get_llm()






    def run(
        self,
        query:str
    ) -> AgentResult:


        try:


            prompt=f"""

你是一个Windows网络自动修复专家。


用户问题:

{query}



请根据问题生成修复方案。


要求:

1. 分析可能原因

2. 给出排查步骤

3. 给出Windows命令

4. 命令必须安全

5. 使用JSON格式返回



格式:

{{
 "reason":"",
 "steps":[],
 "commands":[
    {{
      "command":"",
      "description":""
    }}
 ]
}}


"""



            answer = self.llm.chat(

                prompt

            )



            return AgentResult(

                agent=self.name,

                success=True,

                data={

                    "repair_plan":
                    answer

                },

                message="修复方案生成完成"

            )




        except Exception as e:


            return AgentResult(

                agent=self.name,

                success=False,

                data={},

                message=str(e)

            )