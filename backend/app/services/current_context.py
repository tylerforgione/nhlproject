from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import CurrentContextUnavailable
from app.models.game import Game
from app.models.season import Season
from app.schemas.common import Capability, CapabilityState
from app.schemas.current_context import CurrentContextResponse, SeasonPhase


def resolve_current_context(db: Session, official_date: date) -> CurrentContextResponse:
    todays_game = db.scalars(
        select(Game)
        .where(Game.game_date == official_date)
        .order_by(Game.game_type_id.desc())
    ).first()
    active_season = db.scalars(
        select(Season)
        .where(
            Season.standings_start <= official_date,
            Season.standings_end >= official_date,
        )
        .order_by(Season.id.desc())
    ).first()
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

    schedule_season_id = (
        todays_game.season_id
        if todays_game
        else active_season.id
        if active_season
        else upcoming_season_id
    )

    if schedule_season_id is None:
        raise CurrentContextUnavailable

    return CurrentContextResponse(
        official_date=official_date,
        active_season_phase=(
            SeasonPhase.PLAYOFFS
            if todays_game and todays_game.game_type_id == 3
            else SeasonPhase.PRESEASON
            if todays_game and todays_game.game_type_id == 1
            else SeasonPhase.REGULAR_SEASON
            if active_season
            else SeasonPhase.OFFSEASON
        ),
        schedule_season_id=schedule_season_id,
        latest_completed_season_id=latest_completed_season_id,
        games_capability=Capability(
            state=CapabilityState.AVAILABLE,
            explanation=None,
        ),
    )
