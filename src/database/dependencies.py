from src.repository.abstract_repository import (
    AbstractContactsRepository,
)
from src.repository.contacts import PostgresContactRepository
from src.database.db import SessionLocal


def get_repository() -> AbstractContactsRepository:
    return PostgresContactRepository(SessionLocal())
