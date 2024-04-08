import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from sqlalchemy.orm import Session

from src.repository.contacts import PostgresContactRepository
from src.database.models import Contact
from src.schemas import ContactOut, ContactIn, UserOut, UserIn


class TestPostgresContactRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.sesion = MagicMock(spec=Session)
        self.users_repository = PostgresContactRepository(self.sesion)
        self.user = UserOut(
            id=1,
            username="testuser",
            email="test@example.com",
            password="Pass123!",
            salt="somesalt",
            created_at=datetime.now(),
            avatar="Avatar",
        )

    # get_contacts
    async def test_get_contacts_success(self):
        contacts = [Contact(), Contact(), Contact()]
        self.sesion.query().filter().all.return_value = contacts
        actual_contacts = await self.users_repository.get_contacts(
            search_name="",
            search_email="",
            upcoming_birthdays=False,
            user=self.user,
        )
        self.assertEqual(contacts, actual_contacts)


if __name__ == "__main__":
    unittest.main()
