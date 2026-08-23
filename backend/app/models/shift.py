from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    UniqueConstraint,
    Index,
)

from app.db.base import Base


class Shift(Base):
    __tablename__ = "shifts"

    # NHL shift-chart record ID.
    #
    # This uniquely identifies the API row, but the NHL can
    # occasionally return multiple IDs representing the exact
    # same real-world shift interval.
    id = Column(
        Integer,
        primary_key=True,
    )

    game_id = Column(
        Integer,
        ForeignKey("games.id"),
        nullable=False,
        index=True,
    )

    player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=False,
        index=True,
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    period = Column(
        Integer,
        nullable=False,
    )

    shift_number = Column(Integer)

    start_time_seconds = Column(
        Integer,
        nullable=False,
    )

    end_time_seconds = Column(
        Integer,
        nullable=False,
    )

    duration_seconds = Column(Integer)

    __table_args__ = (
        # Represents one actual player-on-ice interval.
        #
        # NHL occasionally supplies duplicate rows with
        # different IDs / shift numbers for the exact same
        # interval. Those should only be stored once.
        UniqueConstraint(
            "game_id",
            "player_id",
            "period",
            "start_time_seconds",
            "end_time_seconds",
            name="uq_shift_game_player_period_start_end",
        ),
        # Useful for:
        #
        # "Who was on the ice at time X?"
        Index(
            "ix_shifts_game_period_start_end",
            "game_id",
            "period",
            "start_time_seconds",
            "end_time_seconds",
        ),
        # Useful for player-specific game shift queries.
        Index(
            "ix_shifts_player_game",
            "player_id",
            "game_id",
        ),
    )
