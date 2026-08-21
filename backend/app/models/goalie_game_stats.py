from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)

from app.db.base import Base


class GoalieGameStats(Base):
    __tablename__ = "goalie_game_stats"

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

    starter = Column(Boolean)

    # W / L / OTL, sometimes absent
    decision = Column(String(3))

    pim = Column(Integer)

    goals_against = Column(Integer)

    even_strength_goals_against = Column(Integer)
    power_play_goals_against = Column(Integer)
    shorthanded_goals_against = Column(Integer)

    saves = Column(Integer)
    shots_against = Column(Integer)
    save_pctg = Column(Float)

    even_strength_saves = Column(Integer)
    even_strength_shots_against = Column(Integer)

    power_play_saves = Column(Integer)
    power_play_shots_against = Column(Integer)

    shorthanded_saves = Column(Integer)
    shorthanded_shots_against = Column(Integer)

    toi_seconds = Column(Integer)

    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "player_id",
            name="uq_goalie_game_stats_game_player",
        ),
    )
