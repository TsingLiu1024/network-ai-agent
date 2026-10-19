from pathlib import Path


class DocumentLoader:
    def load(self, path):
        return Path(path).read_text(encoding="utf-8")

    def documents(self, config):
        root = config.KNOWLEDGE_PATH
        if not root.is_dir():
            raise ValueError("knowledge directory missing")
        documents, total = [], 0
        for file in sorted(root.rglob("*")):
            if file.suffix.lower() not in {".txt", ".md"} or not file.is_file():
                continue
            # Do not ingest symlinked files/directories outside the configured corpus.
            if file.is_symlink() or not file.resolve().is_relative_to(root.resolve()):
                raise ValueError("knowledge symlinks outside corpus are unsupported")
            size = file.stat().st_size
            total += size
            if size > config.RAG_MAX_FILE_BYTES or total > config.RAG_MAX_TOTAL_BYTES:
                raise ValueError("knowledge size limit exceeded")
            text = file.read_text(encoding="utf-8").strip()
            if text:
                documents.append({"source": file.relative_to(root).as_posix(), "text": text})
        if not documents:
            raise ValueError("knowledge is empty")
        return documents
