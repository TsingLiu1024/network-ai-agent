from pathlib import Path

from langchain_community.vectorstores import FAISS

from .embedding import get_embedding



# 项目根目录
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



class VectorStore:


    def __init__(self):

        self.embedding = (
            get_embedding()
        )



    def create(
        self,
        documents
    ):


        if not documents:


            documents = [

                """
                Network AI Agent default knowledge.

                DNS
                WSL
                Proxy
                Network connectivity.

                """

            ]



        db = FAISS.from_texts(

            documents,

            self.embedding

        )


        VECTOR_DB.mkdir(

            parents=True,

            exist_ok=True

        )


        db.save_local(

            str(VECTOR_DB)

        )


        return db



    def load(self):


        return FAISS.load_local(

            str(VECTOR_DB),

            self.embedding,

            allow_dangerous_deserialization=True

        )