from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    UniqueConstraint,
)

from app.db.base import Base


class SkaterGameStats(Base):
    __tablename__ = "skater_game_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)

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

    sweater_number = Column(Integer)

    position_code = Column(String(2))

    goals = Column(Integer)
    assists = Column(Integer)
    points = Column(Integer)

    plus_minus = Column(Integer)
    pim = Column(Integer)

    hits = Column(Integer)

    power_play_goals = Column(Integer)

    shots_on_goal = Column(Integer)

    faceoff_winning_pctg = Column(Float)

    toi_seconds = Column(Integer)

    blocked_shots = Column(Integer)

    shifts = Column(Integer)

    giveaways = Column(Integer)
    takeaways = Column(Integer)

    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "player_id",
            name="uq_skater_game_stats_game_player",
        ),
    )
