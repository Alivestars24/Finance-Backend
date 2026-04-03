from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)

    records = relationship("Record", back_populates="owner")


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    type = Column(String)  # income / expense
    category = Column(String)
    date = Column(Date)
    notes = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="records")