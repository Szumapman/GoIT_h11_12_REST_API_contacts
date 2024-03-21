from src.repository.abstract_repository import (
    AbstractContactsRepository,
    AbstractUsersRepository,
)

from src.repository.contacts import PostgresContactRepository
from src.repository.users import PostgresUserRepository
from src.database.db import SessionLocal


def get_contact_repository() -> AbstractContactsRepository:
    return PostgresContactRepository(SessionLocal())


def get_user_repository() -> AbstractUsersRepository:
    return PostgresUserRepository(SessionLocal())
