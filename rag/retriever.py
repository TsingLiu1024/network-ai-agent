from pathlib import Path


from .vectorstore import VectorStore

from .builder import RAGBuilder



BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)


VECTOR_DB = (
    BASE_DIR
    /
    "vector_db"
)




class Retriever:


    def __init__(self):


        # 检查向量库是否存在

        if not VECTOR_DB.exists():

            print(
                "Vector database missing."
            )

            print(
                "Building RAG database..."
            )


            RAGBuilder().build()



        self.db = (

            VectorStore()

            .load()

        )




    def search(
        self,
        query
    ):


        docs = (

            self.db

            .similarity_search(

                query,

                k=3

            )

        )



        return [

            doc.page_content

            for doc in docs

        ]