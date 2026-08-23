from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.current_context import CurrentContextResponse
from app.services.current_context import resolve_current_context

router = APIRouter(prefix="/api/v1", tags=["current context"])


@router.get("/current-context", response_model=CurrentContextResponse)
def get_current_context(db: Session = Depends(get_db)) -> CurrentContextResponse:
    return resolve_current_context(db, date.today())
