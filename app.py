"""
Network AI Agent
FastAPI Application Entry

功能:
- Multi-Agent AI 网络诊断系统
- RAG知识检索
- LLM Provider切换
- 自动修复建议
- Tool执行
"""


from contextlib import asynccontextmanager

from fastapi import FastAPI


# API
from api import router
from api.errors import global_exception_handler


# Config
from config.startup import check_startup


# Agent
from agents.core.manager import AgentManager




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期管理

    启动:
        - 环境检查
        - LLM配置检查
        - 初始化Agent系统

    关闭:
        - 释放资源
    """


    print("=" * 60)
    print("Starting Network AI Agent...")
    print("=" * 60)


    # -------------------------
    # Startup Check
    # -------------------------

    if not check_startup():

        raise RuntimeError(
            "Startup check failed."
            "Please check your configuration."
        )


    # -------------------------
    # Initialize Agent System
    # -------------------------

    print(
        "Initializing Agent System..."
    )


    app.state.agent_manager = AgentManager()


    print(
        "Agent System Ready."
    )


    print("=" * 60)



    # 交给FastAPI运行

    yield



    # -------------------------
    # Shutdown
    # -------------------------

    print(
        "Shutting down Network AI Agent..."
    )


    app.state.agent_manager = None





# ==================================================
# FastAPI Instance
# ==================================================


app = FastAPI(

    title="Network AI Agent",

    description="""

    Multi-Agent AI Network Diagnosis System


    Features:

    - Multi-Agent Collaboration

    - RAG Knowledge Retrieval

    - Ollama / DeepSeek / OpenAI Support

    - Automatic Repair Suggestions

    - Network Troubleshooting

    - WSL/OpenWRT Diagnosis

    """,

    version="2.0.0",

    lifespan=lifespan

)





# ==================================================
# Exception Handler
# ==================================================


app.add_exception_handler(

    Exception,

    global_exception_handler

)





# ==================================================
# Router
# ==================================================


app.include_router(

    router

)





# ==================================================
# Basic API
# ==================================================


@app.get("/")
def root():

    return {

        "name":
        "Network AI Agent",

        "version":
        "2.0.0",

        "description":
        "Multi-Agent AI Network Diagnosis System",

        "status":
        "running"

    }





@app.get("/health")
def health():

    return {

        "status":
        "healthy",

        "service":
        "network-ai-agent"

    }





# ==================================================
# Local Run
# ==================================================


if __name__ == "__main__":

    import uvicorn


    uvicorn.run(

        "app:app",

        host="0.0.0.0",

        port=8000,

        reload=True

    )