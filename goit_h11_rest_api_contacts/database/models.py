from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    phone = Column(String(50), nullable=False, unique=True)
    birth_date = Column(DateTime, nullable=False)
    additional_info = Column(JSON, nullable=True)
