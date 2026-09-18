from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request
)


from .schema import (
    DiagnoseRequest,
    DiagnoseResponse
)


from agents.core.manager import AgentManager



router = APIRouter(

    prefix="/api/v1",

    tags=["AI Diagnosis"]

)



def get_agent_manager(
    request: Request
) -> AgentManager:

    """
    从 FastAPI state 获取 AgentManager
    """

    return request.app.state.agent_manager



@router.post(
    "/diagnose",
    response_model=DiagnoseResponse
)
async def diagnose(

    request: DiagnoseRequest,

    manager: AgentManager = Depends(
        get_agent_manager
    )

):


    try:

        result = manager.run(
            request.question
        )


        return DiagnoseResponse(

            success=True,

            question=request.question,

            result=result

        )


    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )