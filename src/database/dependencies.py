from src.repository.abstract_repository import (
    AbstractContactsRepository,
    AbstractUsersRepository,
)

from src.repository.contacts import PostgresContactRepository
from src.repository.users import PostgresUserRepository
from src.database.db import SessionLocal


def get_contact_repository() -> AbstractContactsRepository:
    """
    Returns an instance of the PostgresContactRepository, which implements the AbstractContactsRepository interface.
    The repository is initialized with a session from the SessionLocal database connection.
    """
    return PostgresContactRepository(SessionLocal())


def get_user_repository() -> AbstractUsersRepository:
    """
    Returns an instance of the PostgresUserRepository, which implements the AbstractUsersRepository interface.
    The repository is initialized with a session from the SessionLocal database connection.
    """
    return PostgresUserRepository(SessionLocal())
