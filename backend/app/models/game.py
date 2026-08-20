from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
)

from app.db.base import Base


class Game(Base):
    __tablename__ = "games"

    # NHL game ID, e.g. 2025020001
    id = Column(Integer, primary_key=True)

    season_id = Column(
        Integer,
        ForeignKey("seasons.id"),
        nullable=False,
        index=True,
    )

    # 1 = preseason
    # 2 = regular season
    # 3 = playoffs
    game_type_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    game_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    start_time_utc = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    home_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    away_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    venue = Column(String(100))

    venue_timezone = Column(String(50))

    neutral_site = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Examples:
    # FUT, LIVE, OFF, FINAL
    game_state = Column(String(10))

    # Usually values such as OK
    game_schedule_state = Column(String(10))
