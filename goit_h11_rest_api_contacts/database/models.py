from sqlalchemy import Column, Integer, String, Boolean, func, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(150), nullable=False)
    lastname = Column(String(150), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone = Column(String(50), nullable=False, unique=True)
    birth_date = Column('birth_date', DateTime, nullable=False)
    additional_info = Column(String(1000), nullable=True)

