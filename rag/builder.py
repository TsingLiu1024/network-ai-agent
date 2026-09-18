from pathlib import Path

from .loader import DocumentLoader
from .splitter import TextSplitter
from .vectorstore import VectorStore


class RAGBuilder:


    def build(self):


        loader = DocumentLoader()

        splitter = TextSplitter()

        store = VectorStore()


        # 项目根目录
        base_dir = (
            Path(__file__)
            .resolve()
            .parent.parent
        )


        knowledge_file = (
            base_dir
            /
            "knowledge"
            /
            "network_docs.txt"
        )


        print(
            f"Loading knowledge: {knowledge_file}"
        )


        text = loader.load(
            str(knowledge_file)
        )


        chunks = splitter.split(
            text
        )


        print(
            f"Knowledge chunks: {len(chunks)}"
        )


        store.create(
            chunks
        )


        print(
            "Vector database created."
        )


        return True