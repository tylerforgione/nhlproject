from sqlalchemy import Integer, String, Column, Boolean
from app.db.base import Base


class Season(Base):
    __tablename__ = "season"
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    conferences_in_use = Column(Boolean)
    divisions_in_use = Column(Boolean)
    point_for_ot_loss_in_use = Column(Boolean)
    regulation_wins_in_use = Column(Boolean)
    row_in_use = Column(Boolean)
    standings_end = Column(String(10))
    standings_start = Column(String(10))
    ties_in_use = Column(Boolean)
    wildcard_in_use = Column(Boolean)
