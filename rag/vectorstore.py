"""Safe immutable JSON snapshots; FAISS indices are built in memory.

No pickle or external FAISS binary is deserialized. JSON documents and vectors
are bounded and validated before building the in-memory index. The corpus and
vector volume must be writable only by trusted service administrators.
"""

import hashlib
import json
import os
import re
import uuid
from pathlib import Path

from filelock import FileLock

from config.settings import settings

from .embedding import get_embedding
from .loader import DocumentLoader
from .splitter import TextSplitter

MAX_SNAPSHOT_BYTES = 64_000_000


class VectorStore:
    def __init__(self, config=None, embedding=None):
        self.config = config or settings
        self.embedding = embedding
        self.index = None
        self.documents = []

    def prepare(self):
        import faiss
        import numpy as np

        config = self.config
        root = config.VECTOR_DB_PATH
        root.mkdir(parents=True, exist_ok=True)
        with FileLock(str(root / ".build.lock"), timeout=config.RAG_LOCK_TIMEOUT):
            docs = DocumentLoader().documents(config)
            fingerprint = hashlib.sha256(
                json.dumps(
                    {
                        "documents": docs,
                        "model": config.EMBEDDING_MODEL,
                        "format": 1,
                        "chunk_size": 700,
                        "overlap": 100,
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                ).encode("utf-8")
            ).hexdigest()
            snapshot = None
            try:
                if (root / "CURRENT").stat().st_size > 100:
                    raise ValueError("Invalid generation pointer")
                pointer = (root / "CURRENT").read_text(encoding="ascii").strip()
                if not re.fullmatch(r"[0-9a-f]{64}\.json", pointer):
                    raise ValueError("Invalid generation")
                path = root / pointer
                if path.stat().st_size > MAX_SNAPSHOT_BYTES:
                    raise ValueError("Snapshot too large")
                raw = path.read_bytes()
                if hashlib.sha256(raw).hexdigest() + ".json" != pointer:
                    raise ValueError("Snapshot checksum mismatch")
                candidate = json.loads(raw)
                if not isinstance(candidate, dict) or candidate.get("fingerprint") != fingerprint:
                    raise ValueError("Stale generation")
                self._validate(candidate, np)
                snapshot = candidate
            except (OSError, ValueError, TypeError, KeyError, RecursionError):
                pass
            if self.embedding is None:
                self.embedding = get_embedding(config)
            if snapshot is None:
                chunks = TextSplitter().documents(docs)
                snapshot = {
                    "fingerprint": fingerprint,
                    "documents": chunks,
                    "vectors": self.embedding.embed_documents([d["text"] for d in chunks]),
                }
                self._validate(snapshot, np)
                raw = json.dumps(snapshot, ensure_ascii=False, allow_nan=False).encode("utf-8")
                if len(raw) > MAX_SNAPSHOT_BYTES:
                    raise ValueError("Snapshot size limit exceeded")
                generation = hashlib.sha256(raw).hexdigest() + ".json"
                temporary = root / (uuid.uuid4().hex + ".tmp")
                try:
                    temporary.write_bytes(raw)
                    os.replace(temporary, root / generation)
                    temporary.write_text(generation, encoding="ascii")
                    os.replace(temporary, root / "CURRENT")
                finally:
                    temporary.unlink(missing_ok=True)
                # Readers load under the same lock; after publication old snapshots can go.
                for old in root.glob("*.json"):
                    if old.name != generation and re.fullmatch(r"[0-9a-f]{64}\.json", old.name):
                        old.unlink(missing_ok=True)
            vectors = np.asarray(snapshot["vectors"], dtype="float32")
            faiss.normalize_L2(vectors)
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
            self.documents = snapshot["documents"]
            self.index = index
        return self

    @staticmethod
    def _validate(snapshot, np):
        docs = snapshot["documents"]
        vectors = snapshot["vectors"]
        if not isinstance(docs, list) or not 1 <= len(docs) <= 5000:
            raise ValueError("Invalid documents")
        for doc in docs:
            if (
                not isinstance(doc, dict)
                or not isinstance(doc.get("text"), str)
                or not 1 <= len(doc["text"]) <= 700
                or not isinstance(doc.get("source"), str)
                or len(doc["source"]) > 1000
                or Path(doc["source"]).is_absolute()
                or ".." in Path(doc["source"]).parts
                or not isinstance(doc.get("chunk_id"), int)
            ):
                raise ValueError("Invalid document metadata")
        if not isinstance(vectors, list) or len(vectors) != len(docs):
            raise ValueError("Vector count mismatch")
        if not all(isinstance(v, list) and 1 <= len(v) <= 4096 for v in vectors):
            raise ValueError("Invalid vector dimensions")
        if not all(
            type(number) in (int, float) and -1e6 <= number <= 1e6
            for vector in vectors
            for number in vector
        ):
            raise ValueError("Invalid vector scalars")
        try:
            matrix = np.asarray(vectors, dtype="float32")
        except (OverflowError, TypeError) as exc:
            raise ValueError("Invalid vector scalars") from exc
        if (
            matrix.ndim != 2
            or not np.isfinite(matrix).all()
            or (np.linalg.norm(matrix, axis=1) == 0).any()
        ):
            raise ValueError("Invalid vectors")

    def search(self, query):
        import faiss
        import numpy as np

        if self.index is None:
            raise RuntimeError("RAG must be prepared before search")
        vector = np.asarray([self.embedding.embed_query(query)], dtype="float32")
        if vector.shape != (1, self.index.d) or not np.isfinite(vector).all():
            raise ValueError("Invalid query embedding")
        faiss.normalize_L2(vector)
        scores, indices = self.index.search(vector, min(self.config.RAG_TOP_K, len(self.documents)))
        return [
            {**self.documents[int(i)], "score": round(float(score), 6)}
            for score, i in zip(scores[0], indices[0], strict=True)
            if i >= 0 and score >= self.config.RAG_MIN_SCORE
        ]
