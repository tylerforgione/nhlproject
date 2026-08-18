from sqlalchemy import Column, Integer, String, Date
from app.db.base import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    sweater_number = Column(Integer)
    position_code = Column(String(1))
    shoots_catches = Column(String(1))
    height_in_inches = Column(Integer)
    weight_in_pounds = Column(Integer)
    height_in_centimeters = Column(Integer)
    weight_in_kilograms = Column(Integer)
    birth_date = Column(Date)
    birth_city = Column(String(100))
    birth_country = Column(String(3))
    birth_state_province = Column(String(100))
    headshot_url = Column(String(255))
