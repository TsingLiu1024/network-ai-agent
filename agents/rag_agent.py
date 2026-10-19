from agents.core.base_agent import BaseAgent
from agents.core.result import AgentResult
from config.settings import settings
from rag import Retriever


class RAGAgent(BaseAgent):
    def __init__(self, config=None, retriever=None):
        super().__init__("rag_agent", "Source-bearing retrieval without repeated inference")
        self.config = config or settings
        self.retriever = retriever or Retriever(self.config)
        self.ready = False
        self.error = None

    def prepare(self):
        if not self.config.ENABLE_RAG:
            return
        try:
            self.retriever.prepare()
            self.ready = True
            self.error = None
        except Exception:
            self.ready = False
            self.error = "RAG preparation failed; check local model and knowledge files"

    def run(self, query):
        if not self.config.ENABLE_RAG:
            return AgentResult(
                self.name, False, message="RAG disabled", metadata={"status": "skipped"}
            )
        if not self.ready:
            return AgentResult(
                self.name,
                False,
                message=self.error or "RAG not prepared",
                metadata={"error_code": "rag_unavailable"},
            )
        try:
            docs = self.retriever.search(query)
            return AgentResult(
                self.name,
                True,
                data={"documents": docs},
                message="Knowledge retrieved",
                metadata={"matched": bool(docs)},
            )
        except Exception:
            return AgentResult(
                self.name,
                False,
                message="Knowledge retrieval failed",
                metadata={"error_code": "rag_unavailable"},
            )
