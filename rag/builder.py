"""Explicit index/model preparation: python -m rag.builder."""

from .vectorstore import VectorStore


class RAGBuilder:
    def __init__(self, config=None, embedding=None):
        self.store = VectorStore(config, embedding)

    def build(self):
        self.store.prepare()
        return True


if __name__ == "__main__":
    RAGBuilder().build()
    print("RAG index prepared.")
