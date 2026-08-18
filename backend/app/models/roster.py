from sqlalchemy import Integer, String, Column, ForeignKey, UniqueConstraint
from app.db.base import Base


class Roster(Base):
    __tablename__ = "rosters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    sweater_number = Column(Integer)
    position_code = Column(String(2))

    __table_args__ = (
        UniqueConstraint(
            "player_id", "team_id", "season_id", name="uq_roster_player_team_season"
        ),
    )
