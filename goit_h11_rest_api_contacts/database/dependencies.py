from goit_h11_rest_api_contacts.repository.abstract_repository import (
    AbstractContactsRepository,
)
from goit_h11_rest_api_contacts.repository.contacts import PostgresContactRepository
from goit_h11_rest_api_contacts.database.db import SessionLocal


def get_repository() -> AbstractContactsRepository:
    return PostgresContactRepository(SessionLocal())
