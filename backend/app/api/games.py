from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.domain.games import GameType
from app.db.base import get_db
from app.schemas.games import GamesByDateResponse
from app.services.games import list_games_by_official_date

router = APIRouter(prefix="/api/v1", tags=["games"])


@router.get("/games", response_model=GamesByDateResponse)
def get_games_by_official_date(
    official_date: date = Query(),
    season_id: int | None = Query(default=None),
    game_type: GameType | None = Query(default=None),
    db: Session = Depends(get_db),
) -> GamesByDateResponse:
    return list_games_by_official_date(
        db,
        official_date,
        season_id=season_id,
        game_type=game_type,
    )
