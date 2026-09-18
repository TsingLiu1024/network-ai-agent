from agents.core.base_agent import BaseAgent
from agents.core.result import AgentResult

from rag import Retriever

from llm import get_llm



class RAGAgent(BaseAgent):


    def __init__(self):


        super().__init__(

            name="rag_agent",

            description="Knowledge retrieval and reasoning agent"

        )


        self.retriever = Retriever()


        self.llm = get_llm()



    def run(

        self,

        query: str

    ) -> AgentResult:


        try:


            # 1. 检索知识库

            docs = (

                self.retriever

                .search(

                    query

                )

            )


            context = "\n\n".join(

                docs

            )



            # 2. 构造Prompt

            prompt = f"""

你是一个专业的网络故障诊断专家。


用户问题:

{query}



知识库内容:

{context}



请根据用户问题和知识库内容进行分析。


输出格式:

问题分析:
xxx


可能原因:
1.xxx
2.xxx


解决方案:
1.xxx
2.xxx


注意:
不要编造不存在的信息。

"""



            # 3. 调用LLM

            answer = (

                self.llm

                .chat(

                    prompt

                )

            )



            return AgentResult(

                agent=self.name,

                success=True,

                data={

                    "documents": docs,

                    "analysis": answer

                },

                message="知识检索与分析完成"

            )



        except Exception as e:



            return AgentResult(

                agent=self.name,

                success=False,

                data={},

                message=f"知识检索失败: {str(e)}"

            )