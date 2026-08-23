from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Float,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base


class GameEvent(Base):
    __tablename__ = "game_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    game_id = Column(
        Integer,
        ForeignKey("games.id"),
        nullable=False,
        index=True,
    )

    event_id = Column(Integer, nullable=False)

    period_number = Column(Integer)
    period_type = Column(String(10))

    time_in_period = Column(String(10))
    time_remaining = Column(String(10))

    situation_code = Column(String(10))
    home_team_defending_side = Column(String(10))

    type_code = Column(Integer)
    event_type = Column(String(50))

    sort_order = Column(Integer)

    event_owner_team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=True,
        index=True,
    )

    x_coord = Column(Float)
    y_coord = Column(Float)
    zone_code = Column(String(2))

    details = Column(JSONB)

    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "event_id",
            name="uq_game_events_game_event",
        ),
    )
