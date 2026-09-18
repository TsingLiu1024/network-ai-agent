"""
Agent Manager

负责:
- 管理所有Agent
- Agent调度
- RAG增强
- 汇总诊断结果
- Supervisor最终总结
"""


from agents.network_agent import NetworkAgent
from agents.log_agent import LogAgent
from agents.rag_agent import RAGAgent
from agents.repair_agent import RepairAgent

from agents.core.supervisor_agent import SupervisorAgent



class AgentManager:


    def __init__(self):


        self.agents = {

            "network":
            NetworkAgent(),


            "log":
            LogAgent(),


            "rag":
            RAGAgent(),


            "repair":
            RepairAgent()

        }


        # 最终总结Agent
        self.supervisor = SupervisorAgent()



    def get_agent(
        self,
        name: str
    ):

        return self.agents.get(name)




    def run(
        self,
        query: str
    ):


        results = {}



        # =========================
        # 1. RAG知识检索
        # =========================

        try:


            rag_result = self.agents["rag"].run(
                query
            )


            results["rag"] = (
                rag_result.to_dict()
            )


            context = ""


            if rag_result.success:


                documents = (
                    rag_result
                    .data
                    .get(
                        "documents",
                        []
                    )
                )


                context = "\n".join(
                    documents
                )



        except Exception as e:


            results["rag"] = {

                "success":
                False,

                "error":
                str(e)

            }


            context = ""




        # =========================
        # 2. 网络诊断
        # =========================


        for name in [
            "network",
            "log"
        ]:


            try:


                result = (
                    self.agents[name]
                    .run(query)
                )


                results[name] = (
                    result.to_dict()
                )


            except Exception as e:


                results[name] = {


                    "success":
                    False,


                    "error":
                    str(e)

                }




        # =========================
        # 3. Repair Agent
        # =========================


        repair_context = f"""

用户问题:

{query}


网络检测:

{results.get("network")}


日志分析:

{results.get("log")}


知识库:

{context}

"""


        try:


            repair_result = (
                self.agents["repair"]
                .run(
                    repair_context
                )
            )


            results["repair"] = (
                repair_result.to_dict()
            )


        except Exception as e:


            results["repair"] = {


                "success":
                False,


                "error":
                str(e)

            }





        # =========================
        # 4. Supervisor总结
        # =========================


        try:


            supervisor_result = (
                self.supervisor.run(

                    query,

                    results

                )
            )


            results["supervisor"] = (
                supervisor_result.to_dict()
            )



        except Exception as e:


            results["supervisor"] = {


                "success":
                False,


                "error":
                str(e)

            }



        return results