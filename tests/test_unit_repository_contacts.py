import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.repository.contacts import PostgresContactRepository
from tests.data_set_for_tests import (
    user_out,
    contact,
    contact_2,
    contact_in,
    contact_out,
    contact_out_2,
    get_contacts_success_test_cases,
    get_contacts_exception_too_many_arguments_test_cases,
)


def mock_refresh(contact_to_refresh):
    contact_to_refresh.id = 1


class TestPostgresContactRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.users_repository = PostgresContactRepository(self.session)
        self.session.refresh = mock_refresh

    async def test_get_contacts_success(self):
        contacts_to_query = [contact, contact_2]
        contacts_out = [contact_out, contact_out_2]
        self.session.query().filter().all.return_value = contacts_to_query
        for test_case in get_contacts_success_test_cases:
            actual_contacts = await self.users_repository.get_contacts(
                search_name=test_case["search_name"],
                search_email=test_case["search_email"],
                upcoming_birthdays=test_case["upcoming_birthdays"],
                user=user_out,
            )
            self.assertEqual(contacts_out, actual_contacts)

    async def test_get_contacts_exception_too_many_arguments(self):
        for test_case in get_contacts_exception_too_many_arguments_test_cases:
            with self.assertRaises(HTTPException) as context:
                await self.users_repository.get_contacts(
                    search_name=test_case["search_name"],
                    search_email=test_case["search_email"],
                    upcoming_birthdays=test_case["upcoming_birthdays"],
                    user=user_out,
                )
            self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_get_contact_success(self):
        self.session.query().filter().first.return_value = contact
        actual_contact = await self.users_repository.get_contact(
            contact_id=contact.id, user=user_out
        )
        self.assertEqual(contact.id, actual_contact.id)
        self.assertEqual(contact.first_name, actual_contact.first_name)
        self.assertEqual(contact.last_name, actual_contact.last_name)
        self.assertEqual(contact.email, actual_contact.email)
        self.assertEqual(contact.phone, actual_contact.phone)
        self.assertEqual(contact.birth_date.date(), actual_contact.birth_date)

    async def test_get_contact_not_found(self):
        contact_none = None
        self.session.query().filter().first.return_value = contact_none

        with self.assertRaises(HTTPException) as context:
            await self.users_repository.get_contact(contact_id=404, user=user_out)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    # create_contact
    async def test_create_contact_success(self):
        # self.session.refresh = mock_refresh

        actual_contact = await self.users_repository.create_contact(
            contact_in, user_out
        )
        self.assertEqual(contact_in.first_name, actual_contact.first_name)
        self.assertEqual(contact_in.last_name, actual_contact.last_name)
        self.assertEqual(contact_in.email, actual_contact.email)
        self.assertEqual(contact_in.phone, actual_contact.phone)
        self.assertEqual(contact_in.birth_date, actual_contact.birth_date)

    async def test_update_contact_success(self):
        self.session.query().filter().first.return_value = contact
        contact_in.first_name = "new_first_name"
        contact_in.last_name = "new_last_name"
        contact_in.email = "new_email@example.com"
        contact_in.phone = "+48550550500"
        contact_in.birth_date = date(2000, 1, 1)
        actual_contact = await self.users_repository.update_contact(
            contact_id=contact.id, contact=contact_in, user=user_out
        )
        self.assertEqual(contact_in.first_name, actual_contact.first_name)
        self.assertEqual(contact_in.last_name, actual_contact.last_name)
        self.assertEqual(contact_in.email, actual_contact.email)
        self.assertEqual(contact_in.phone, actual_contact.phone)
        self.assertEqual(contact_in.birth_date, actual_contact.birth_date)

    async def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await self.users_repository.update_contact(
                contact_id=404, contact=contact_in, user=user_out
            )
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_delete_contact_success(self):
        self.session.query().filter().first.return_value = contact
        actual_contact = await self.users_repository.delete_contact(
            contact_id=contact.id, user=user_out
        )
        self.assertEqual(contact.id, actual_contact.id)
        self.session.delete.assert_called_once_with(contact)
        self.session.commit.assert_called_once()

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await self.users_repository.delete_contact(contact_id=404, user=user_out)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
