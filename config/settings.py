import os

from dotenv import load_dotenv



load_dotenv()




class Settings:


    # ======================
    # LLM Provider
    # ======================


    MODEL_PROVIDER = os.getenv(

        "LLM_PROVIDER",

        "ollama"

    ).lower()



    # ======================
    # Ollama
    # ======================


    OLLAMA_URL = os.getenv(

        "OLLAMA_URL",

        "http://localhost:11434"

    )



    OLLAMA_MODEL = os.getenv(

        "OLLAMA_MODEL",

        "deepseek-r1:7b"

    )




    # ======================
    # DeepSeek
    # ======================


    DEEPSEEK_API_KEY = os.getenv(

        "DEEPSEEK_API_KEY"

    )



    DEEPSEEK_BASE_URL = os.getenv(

        "DEEPSEEK_BASE_URL",

        "https://api.deepseek.com"

    )



    DEEPSEEK_MODEL = os.getenv(

        "DEEPSEEK_MODEL",

        "deepseek-chat"

    )




    # ======================
    # OpenAI
    # ======================


    OPENAI_API_KEY = os.getenv(

        "OPENAI_API_KEY"

    )



    OPENAI_BASE_URL = os.getenv(

        "OPENAI_BASE_URL",

        "https://api.openai.com/v1"

    )



    OPENAI_MODEL = os.getenv(

        "OPENAI_MODEL",

        "gpt-5"

    )




    # ======================
    # RAG
    # ======================


    VECTOR_DB_PATH = os.getenv(

        "VECTOR_DB_PATH",

        "vector_db"

    )



    KNOWLEDGE_PATH = os.getenv(

        "KNOWLEDGE_PATH",

        "knowledge"

    )





    # ======================
    # Token Optimizer
    # ======================


    ENABLE_TOKEN_OPTIMIZER = (

        os.getenv(

            "ENABLE_TOKEN_OPTIMIZER",

            "true"

        )
        .lower()

        ==
        "true"

    )



    MAX_CONTEXT_LENGTH = int(

        os.getenv(

            "MAX_CONTEXT_LENGTH",

            "4000"

        )

    )





settings = Settings()