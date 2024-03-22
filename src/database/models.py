from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    func,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("email", "user_id", name="unique_email_user"),
        UniqueConstraint("phone", "user_id", name="unique_phone_user"),
    )
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    additional_info = Column(JSON, nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(150), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    created_at = Column("created_at", DateTime, default=func.now())
    refresh_token = Column(String(255), nullable=True)
