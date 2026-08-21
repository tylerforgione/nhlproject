from sqlalchemy import Integer, String, Column, Boolean
from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    abbrev = Column(String(5), nullable=False)
    logo = Column(String(255))
    dark_logo = Column(String(255))
    first_season = Column(String(8))
    last_season = Column(String(8))
    is_active = Column(Boolean, default=False)
    is_nhl = Column(Boolean, default=True)
