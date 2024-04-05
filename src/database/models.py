from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    func,
    UniqueConstraint,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Contact(Base):
    """
    Represents a contact in the database.

    Attributes:
        id (int): Primary key for the contact.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email address of the contact (unique per user).
        phone (str): Phone number of the contact (unique per user).
        birth_date (datetime): Birth date of the contact.
        additional_info (dict): Additional information about the contact (stored as JSON).
        user_id (int): Foreign key referencing the associated user.
        user (User): Relationship to the associated user (one-to-many).

    Table Name:
        "contacts"

    Constraints:
        - Unique constraint on (email, user_id)
        - Unique constraint on (phone, user_id)
    """
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
    """
    Represents a user in the database.

    Attributes:
        id (int): Primary key for the user.
        username (str): Username of the user (unique).
        email (str): Email address of the user (unique).
        password (str): Hashed password of the user.
        salt (str): Salt used for password hashing.
        created_at (datetime): Timestamp of user creation.
        refresh_token (str): Refresh token for authentication (nullable).
        confirmed (bool): Flag indicating if the user's email is confirmed.
        avatar (str): URL to the user's avatar image (nullable).

    Table Name:
        "users"
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(150), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    salt = Column(String(32), nullable=False)
    created_at = Column("created_at", DateTime, default=func.now())
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)
