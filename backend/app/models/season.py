from sqlalchemy import Integer, Date, Column, Boolean
from app.db.base import Base


class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True)
    conferences_in_use = Column(Boolean)
    divisions_in_use = Column(Boolean)
    point_for_ot_loss_in_use = Column(Boolean)
    regulation_wins_in_use = Column(Boolean)
    row_in_use = Column(Boolean)
    standings_end = Column(Date, nullable=False)
    standings_start = Column(Date, nullable=False)
    ties_in_use = Column(Boolean)
    wildcard_in_use = Column(Boolean)
