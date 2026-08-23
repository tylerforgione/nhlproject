from fastapi import Request
from fastapi.responses import JSONResponse

from app.errors import CurrentContextUnavailable


async def current_context_unavailable_handler(
    request: Request, exc: CurrentContextUnavailable
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": [],
            }
        },
    )
