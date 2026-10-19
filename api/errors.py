from fastapi.responses import JSONResponse


async def validation_exception_handler(request, exc):
    # Pydantic normally echoes invalid input, including entire submitted objects.
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "detail": [
                {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
                for error in exc.errors()
            ],
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", None),
        },
    )
