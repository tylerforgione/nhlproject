from sqlalchemy import Integer, Column, Float, String, ForeignKey, UniqueConstraint
from app.db.base import Base


class Standing(Base):
    __tablename__ = "standings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    conference_name = Column(String(50))
    conference_abbrev = Column(String(10))
    division_name = Column(String(50))
    division_abbrev = Column(String(10))
    games_played = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    ot_losses = Column(Integer)
    ties = Column(Integer)
    points = Column(Integer)
    point_pctg = Column(Float)
    goal_for = Column(Integer)
    goal_against = Column(Integer)
    goal_differential = Column(Integer)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    home_ot_losses = Column(Integer)
    road_wins = Column(Integer)
    road_losses = Column(Integer)
    road_ot_losses = Column(Integer)
    regulation_wins = Column(Integer)
    regulation_plus_ot_wins = Column(Integer)
    shootout_wins = Column(Integer)
    shootout_losses = Column(Integer)
    streak_code = Column(String(5))
    streak_count = Column(Integer)
    wildcard_sequence = Column(Integer)
    league_sequence = Column(Integer)
    conference_sequence = Column(Integer)
    division_sequence = Column(Integer)

    __table_args__ = (
        UniqueConstraint("team_id", "season_id", name="uq_standing_team_season"),
    )
