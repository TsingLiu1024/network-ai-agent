from .vectorstore import VectorStore


class Retriever:
    def __init__(self, config=None, embedding=None):
        self.store = VectorStore(config, embedding)

    def prepare(self):
        self.store.prepare()
        return self

    def search(self, query):
        return self.store.search(query)
