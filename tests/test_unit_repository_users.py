import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.repository.users import PostgresUserRepository
from tests.data_set_for_tests import user_out, user_in, user, salt, created_at_set


def mock_refresh(user_to_refresh):
    user_to_refresh.id = 1
    user_to_refresh.created_at = created_at_set


class TestPostgresUserRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.users_repository = PostgresUserRepository(self.session)
        self.session.refresh = mock_refresh

    # get_user_by_email
    async def test_get_user_by_email_success(self):
        self.session.query().filter().first.return_value = user_out
        actual_user = await self.users_repository.get_user_by_email(user_out.email)
        self.assertEqual(user_out, actual_user)

    async def test_get_user_by_email_not_found(self):
        email = "not_existing_email@example.com"
        self.session.query().filter().first.return_value = None
        actual_user = await self.users_repository.get_user_by_email(email)
        self.assertIsNone(actual_user)

    async def test_create_user_success(self):
        created_user = await self.users_repository.create_user(user_in, salt)

        self.assertEqual(user_in.username, created_user.username)
        self.assertEqual(user_in.email, created_user.email)
        self.assertEqual(user_in.password, created_user.password)
        self.assertEqual(salt, created_user.salt)
        self.assertEqual(created_at_set, created_user.created_at)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()

    @patch("libgravatar.Gravatar.get_image")
    async def test_create_user_gravatar_exception(self, mock_gravatar):
        mock_gravatar.side_effect = Exception

        with self.assertRaises(Exception):
            await self.users_repository.create_user(user_in, salt)

    async def test_update_token_success(self):
        token = "some_token"
        await self.users_repository.update_token(user, token)
        self.session.commit.assert_called_once()

    async def test_confirm_email_success(self):
        await self.users_repository.confirm_email(user.email)
        self.session.commit.assert_called_once()

    async def test_confirm_email_not_found(self):
        email = "not_existing_email@example.com"
        self.session.query().filter(email).first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await self.users_repository.confirm_email(email)
        self.session.commit.assert_not_called()
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_update_avatar_success(self):
        new_avatar = "url_to_new_avatar"
        self.session.query().filter(user.email).first.return_value = user
        updated_user = await self.users_repository.update_avatar(user.email, new_avatar)
        self.session.commit.assert_called_once()
        self.assertEqual(updated_user.avatar, new_avatar)

    async def test_update_avatar_not_found(self):
        email = "test@example.com"
        self.session.query().filter(email).first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await self.users_repository.update_avatar(email, "avatar.jpg")
        self.session.commit.assert_not_called()
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_update_password_success(self):
        new_password = "Pass234!"
        await self.users_repository.update_password(user.email, new_password, salt)
        self.session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
