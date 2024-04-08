import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException, status


from src.database.models import User
from src.schemas import UserIn, UserOut
from src.repository.users import PostgresUserRepository


class TestPostgresUserRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.users_repository = PostgresUserRepository(self.session)

    # get_user_by_email
    async def test_get_user_by_email_success(self):
        email = "test@example.com"
        expected_user = User(id=1, email=email, password="Pass123$")
        self.session.query().filter().first.return_value = expected_user
        actual_user = await self.users_repository.get_user_by_email(email)
        self.assertEqual(expected_user, actual_user)

    async def test_get_user_by_email_not_found(self):
        email = "test@example.com"
        self.session.query().filter().first.return_value = None
        actual_user = await self.users_repository.get_user_by_email(email)
        self.assertIsNone(actual_user)

    # create_user
    # @patch("libgravatar.Gravatar", autospec=True)
    # async def test_create_user_success(self, gravatar_mock):
    #     created_at_now = datetime.now()
    #     user_in = UserIn(
    #         username="testuser",
    #         email="test@example.com",
    #         password="Pass123!",
    #     )
    #     salt = "somesalt"
    #     new_user = User(
    #         id=1,
    #         username="testuser",
    #         email="test@example.com",
    #         password="Pass123!",
    #         salt="somesalt",
    #         created_at=created_at_now,
    #         avatar="Avatar.jpg",
    #     )
    #     user_out = UserOut(
    #         id=1,
    #         username="testuser",
    #         email="test@example.com",
    #         password="Pass123!",
    #         salt="somesalt",
    #         created_at=created_at_now,
    #         avatar="Avatar.jpg",
    #     )
    #     gravatar_instance = gravatar_mock.return_value
    #     gravatar_instance.get_image.return_value = "Avatar.jpg"
    #
    #     new_user_instance = MagicMock(user_out=user_out)
    #
    #     with patch("src.schemas.UserOut", new_user_instance):
    #         created_user = await self.users_repository.create_user(user_in, salt)
    #
    #     self.session.add.assert_called_once()
    #     self.session.commit.assert_called_once()
    #     self.session.refresh.assert_called_once()
    #
    #     self.assertEqual(created_user, user_out)

    # @patch("libgravatar.Gravatar")
    # async def test_create_user_success(self, mock_gravatar):
    #     user_in = UserIn(
    #         username="testuser", email="test@example.com", password="Password1!"
    #     )
    #     salt = "somesalt"
    #     expected = UserOut(
    #         id=1,
    #         username="testuser",
    #         email="test@example.com",
    #         password="Password1!",
    #         salt="somesalt",
    #         created_at=datetime.now(),
    #         avatar="Avatar",
    #     )
    #
    #     mock_gravatar.return_value.get_image.return_value = "Avatar"
    #
    #     actual = await self.users_repository.create_user(user_in, salt)
    #
    #     self.assertEqual(expected.username, actual.username)
    #     self.assertEqual(expected.email, actual.email)
    #     self.assertEqual(expected.password, actual.password)
    #     self.assertEqual(expected.salt, actual.salt)
    #     self.assertEqual(expected.avatar, actual.avatar)

    async def test_create_user_gravatar_exception(self):
        user_in = UserIn(
            username="testuser", email="test@example.com", password="Password1!"
        )
        salt = "somesalt"

        mock_gravatar = patch("libgravatar.Gravatar")
        mock_gravatar.side_effect = Exception("Gravatar error")

        with self.assertRaises(Exception):
            await self.users_repository.create_user(user_in, salt)

    async def test_confirm_email_success(self):
        email = "test@example.com"
        user = User(id=1, email=email, password="Pass123!")
        self.session.query().filter(User.email == email).first.return_value = user
        await self.users_repository.confirm_email(email)
        self.session.commit.assert_called_once()

    async def test_confirm_email_not_found(self):
        email = "test@example.com"
        self.session.query().filter(User.email == email).first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await self.users_repository.confirm_email(email)
        self.session.commit.assert_not_called()
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_update_avatar_success(self):
        email = "test@example.com"
        user = User(
            id=1,
            username="testuser",
            email=email,
            password="Pass123!",
            salt="somesalt",
            created_at=datetime.now(),
            avatar="old_avatar.jpg",
        )
        avatar = "avatar.jpg"
        self.session.query().filter(User.email == email).first.return_value = user
        updated_user = await self.users_repository.update_avatar(email, avatar)
        self.session.commit.assert_called_once()
        self.assertEqual(updated_user.avatar, avatar)
        self.assertIsInstance(updated_user, UserOut)

    async def test_update_avatar_not_found(self):
        email = "test@example.com"
        self.session.query().filter(User.email == email).first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await self.users_repository.update_avatar(email, "avatar.jpg")
        self.session.commit.assert_not_called()
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_update_password_success(self):
        email = "test@example.com"
        user = User(
            id=1,
            username="testuser",
            email=email,
            password="Pass123!",
            salt="somesalt",
            created_at=datetime.now(),
            avatar="old_avatar.jpg",
        )
        password = "Pass234!"
        salt = "new_salt"
        self.session.query().filter(User.email == email).first.return_value = user
        await self.users_repository.update_password(email, password, salt)
        self.session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
