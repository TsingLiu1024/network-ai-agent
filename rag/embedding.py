"""No model imports or downloads until explicit RAG preparation."""


class SentenceEmbedding:
    def __init__(self, config):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(
            config.EMBEDDING_MODEL,
            local_files_only=config.EMBEDDING_LOCAL_ONLY,
            trust_remote_code=False,
        )

    def embed_documents(self, texts):
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]


def get_embedding(config=None):
    from config.settings import settings

    return SentenceEmbedding(config or settings)
