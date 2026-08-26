from datetime import date, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.games import game_state_from_code, game_type_from_id
from app.models.game import Game
from app.models.game_result import GameResult
from app.models.team import Team
from app.schemas.games import (
    GameSummary,
    GamesByDateResponse,
    TeamReference,
)
from app.services.capabilities import unverified_schedule_capability


def _team_reference(team: Team) -> TeamReference:
    return TeamReference(
        id=team.id,
        name=team.name,
        abbreviation=team.abbrev,
        logo_url=team.logo,
        dark_logo_url=team.dark_logo,
    )


def list_games_by_official_date(
    db: Session, official_date: date
) -> GamesByDateResponse:
    games = db.scalars(
        select(Game)
        .where(Game.game_date == official_date)
        .order_by(Game.start_time_utc.asc(), Game.id.asc())
    ).all()
    summaries = []

    for game in games:
        away_team = db.get(Team, game.away_team_id)
        home_team = db.get(Team, game.home_team_id)
        result = db.get(GameResult, game.id)
        start_time_utc = game.start_time_utc

        if start_time_utc and start_time_utc.tzinfo is None:
            start_time_utc = start_time_utc.replace(tzinfo=timezone.utc)

        summaries.append(
            GameSummary(
                id=game.id,
                season_id=game.season_id,
                game_type=game_type_from_id(game.game_type_id),
                state=game_state_from_code(game.game_state),
                official_date=game.game_date,
                start_time_utc=start_time_utc,
                away_team=_team_reference(away_team),
                home_team=_team_reference(home_team),
                away_score=result.away_team_score if result else None,
                home_score=result.home_team_score if result else None,
                venue=game.venue,
                venue_timezone=game.venue_timezone,
                neutral_site=game.neutral_site,
            )
        )

    return GamesByDateResponse(
        official_date=official_date,
        capability=unverified_schedule_capability(),
        games=summaries,
    )
