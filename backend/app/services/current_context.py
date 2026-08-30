from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.games import GameTypeId
from app.errors import CurrentContextUnavailable
from app.models.game import Game
from app.models.season import Season
from app.schemas.current_context import CurrentContextResponse, SeasonPhase
from app.services.capabilities import unverified_schedule_capability


def _season_id_for_game_type_window(
    db: Session, official_date: date, game_type: GameTypeId
) -> int | None:
    return db.scalar(
        select(Game.season_id)
        .where(Game.game_type_id == game_type)
        .group_by(Game.season_id)
        .having(
            func.min(Game.game_date) <= official_date,
            func.max(Game.game_date) >= official_date,
        )
        .order_by(Game.season_id.desc())
        .limit(1)
    )


def resolve_current_context(db: Session, official_date: date) -> CurrentContextResponse:
    active_season = db.scalars(
        select(Season)
        .where(
            Season.standings_start <= official_date,
            Season.standings_end >= official_date,
        )
        .order_by(Season.id.desc())
    ).first()
    playoff_season_id = _season_id_for_game_type_window(
        db, official_date, GameTypeId.PLAYOFFS
    )
    preseason_season_id = _season_id_for_game_type_window(
        db, official_date, GameTypeId.PRESEASON
    )
    upcoming_season_id = db.scalar(
        select(Season.id)
        .where(Season.standings_start > official_date)
        .order_by(Season.standings_start.asc())
        .limit(1)
    )
    latest_completed_season_id = db.scalar(
        select(Season.id)
        .where(Season.standings_end < official_date)
        .order_by(Season.id.desc())
        .limit(1)
    )

    if playoff_season_id is not None:
        active_season_phase = SeasonPhase.PLAYOFFS
        schedule_season_id = playoff_season_id
    elif preseason_season_id is not None and active_season is None:
        active_season_phase = SeasonPhase.PRESEASON
        schedule_season_id = preseason_season_id
    elif active_season is not None:
        active_season_phase = SeasonPhase.REGULAR_SEASON
        schedule_season_id = active_season.id
    else:
        active_season_phase = SeasonPhase.OFFSEASON
        schedule_season_id = upcoming_season_id

    if schedule_season_id is None:
        raise CurrentContextUnavailable

    return CurrentContextResponse(
        official_date=official_date,
        active_season_phase=active_season_phase,
        schedule_season_id=schedule_season_id,
        latest_completed_season_id=latest_completed_season_id,
        games_capability=unverified_schedule_capability(),
    )
