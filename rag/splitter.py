class TextSplitter:
    def __init__(self, chunk_size=700, chunk_overlap=100):
        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError("Invalid chunk size/overlap")
        self.chunk_size = chunk_size
        self.step = chunk_size - chunk_overlap

    def split(self, text):
        return [text[i : i + self.chunk_size] for i in range(0, len(text), self.step)]

    def documents(self, docs):
        chunks = []
        for doc in docs:
            for number, text in enumerate(self.split(doc["text"])):
                chunks.append({"source": doc["source"], "chunk_id": number, "text": text})
        if len(chunks) > 5000:
            raise ValueError("knowledge chunk limit exceeded")
        return chunks
