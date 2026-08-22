from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)

from app.db.base import Base


class GameResult(Base):
    __tablename__ = "game_results"

    game_id = Column(
        Integer,
        ForeignKey("games.id"),
        primary_key=True,
    )

    home_team_score = Column(Integer)
    away_team_score = Column(Integer)

    home_team_sog = Column(Integer)
    away_team_sog = Column(Integer)

    # Current/final period information
    period_number = Column(Integer)
    period_type = Column(String(10))

    # Current clock state
    time_remaining = Column(String(10))
    seconds_remaining = Column(Integer)

    clock_running = Column(Boolean)
    in_intermission = Column(Boolean)

    # Final outcome type once known:
    # REG / OT / SO
    last_period_type = Column(String(10))
