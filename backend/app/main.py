from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.current_context import router as current_context_router
from app.api.errors import unexpected_error_handler, validation_error_handler
from app.api.games import router as games_router
from app.api.service_errors import current_context_unavailable_handler
from app.errors import CurrentContextUnavailable

app = FastAPI(
    title="NHL Analytics API",
    version="0.1.0"
)

app.include_router(current_context_router)
app.include_router(games_router)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)
app.add_exception_handler(
    CurrentContextUnavailable, current_context_unavailable_handler
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
