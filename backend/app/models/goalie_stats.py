from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    UniqueConstraint,
)

from app.db.base import Base


class GoalieStats(Base):
    __tablename__ = "goalie_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)

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

    season_id = Column(
        Integer,
        ForeignKey("seasons.id"),
        nullable=False,
        index=True,
    )

    game_type_id = Column(Integer, nullable=False)

    games_played = Column(Integer)
    games_started = Column(Integer)

    wins = Column(Integer)
    losses = Column(Integer)
    ties = Column(Integer)
    ot_losses = Column(Integer)

    shots_against = Column(Integer)
    goals_against = Column(Integer)
    goals_against_avg = Column(Float)

    save_pctg = Column(Float)
    shutouts = Column(Integer)

    time_on_ice_seconds = Column(Integer)

    goals = Column(Integer)
    assists = Column(Integer)
    pim = Column(Integer)

    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "team_id",
            "season_id",
            "game_type_id",
            name="uq_goalie_stats_player_team_season_game_type",
        ),
    )
