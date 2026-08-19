from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    UniqueConstraint,
)

from app.db.base import Base


class SkaterStats(Base):
    __tablename__ = "skater_stats"

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

    # 2 = regular season, 3 = playoffs
    game_type_id = Column(Integer, nullable=False)

    games_played = Column(Integer)

    goals = Column(Integer)
    assists = Column(Integer)
    points = Column(Integer)

    plus_minus = Column(Integer)
    pim = Column(Integer)

    shots = Column(Integer)
    shooting_pctg = Column(Float)

    # Stored as seconds instead of API "MM:SS"
    avg_toi_seconds = Column(Integer)

    faceoff_winning_pctg = Column(Float)

    power_play_goals = Column(Integer)
    power_play_points = Column(Integer)

    shorthanded_goals = Column(Integer)
    shorthanded_points = Column(Integer)

    game_winning_goals = Column(Integer)
    ot_goals = Column(Integer)

    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "team_id",
            "season_id",
            "game_type_id",
            name="uq_skater_stats_player_team_season_game_type",
        ),
    )
