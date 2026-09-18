"""
Network Diagnosis Agent

负责:
- 网络状态检测
- 调用LLM分析网络问题
- 输出诊断结果
"""


from agents.core.base_agent import BaseAgent
from agents.core.result import AgentResult

from llm import get_llm



class NetworkAgent(BaseAgent):


    def __init__(self):

        super().__init__(
            name="network_agent",
            description="Network diagnosis agent"
        )


        self.llm = get_llm()



    def run(
        self,
        query: str
    ) -> AgentResult:


        prompt = f"""
你是一名Windows网络故障专家。

用户遇到的问题:

{query}


请分析:

1. 可能原因
2. 排查步骤
3. 修复方案


要求:
- 使用中文
- 输出详细步骤
- 如果涉及DNS、代理、WSL，请重点分析
"""


        try:


            answer = self.llm.chat(
                prompt
            )


            return AgentResult(

                agent=self.name,

                success=True,

                data={

                    "query":query,

                    "analysis":answer

                },

                message="网络智能分析完成"

            )


        except Exception as e:


            return AgentResult(

                agent=self.name,

                success=False,

                data={},

                message=str(e)

            )