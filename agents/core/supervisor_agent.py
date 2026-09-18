"""
Supervisor Agent

负责:
- 汇总多个Agent结果
- 调用LLM生成最终诊断报告
- 作为Agent系统总控
"""


from agents.core.base_agent import BaseAgent
from agents.core.result import AgentResult

from llm import get_llm



class SupervisorAgent(BaseAgent):


    def __init__(self):

        super().__init__(
            name="supervisor_agent",
            description="Supervisor agent for final diagnosis"
        )


        self.llm = get_llm()



    def run(
        self,
        query: str,
        results: dict
    ) -> AgentResult:


        try:


            prompt = f"""
你是一个网络故障诊断专家。

请根据下面的信息生成完整诊断报告。


=========================
用户问题
=========================

{query}



=========================
Agent诊断结果
=========================

{results}



请按照以下格式回答：


## 1. 问题分析

说明可能原因。


## 2. 诊断依据

结合日志、网络检测、知识库。


## 3. 解决方案

给出具体步骤。


## 4. 推荐执行命令

列出Windows/Linux命令。


## 5. 后续建议

说明如何避免再次发生。


请使用中文回答。
"""


            answer = self.llm.chat(
                prompt
            )


            return AgentResult(

                agent=self.name,

                success=True,

                data={

                    "answer": answer

                },

                message="最终诊断生成完成"

            )


        except Exception as e:


            return AgentResult(

                agent=self.name,

                success=False,

                data={},

                message=f"Supervisor执行失败: {str(e)}"

            )