import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from sqlalchemy.orm import Session


from src.database.models import User
from src.schemas import UserIn, UserOut
from src.repository.users import PostgresUserRepository


class TestPostgresUserRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.sesion = MagicMock(spec=Session)
        self.users_repository = PostgresUserRepository(self.sesion)

    # get_user_by_email
    async def test_get_user_by_email_success(self):
        email = "test@example.com"
        expected_user = User(id=1, email=email, password="Pass123$")
        self.sesion.query().filter().first.return_value = expected_user
        actual_user = await self.users_repository.get_user_by_email(email)
        self.assertEqual(expected_user, actual_user)

    async def test_get_user_by_email_not_found(self):
        email = "test@example.com"
        self.sesion.query().filter().first.return_value = None
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

    #     new_user_instance = MagicMock(spec=User)
    #     new_user_instance.return_value = new_user

    #     with patch("src.database.models.User", return_value=new_user_instance):
    #         created_user = await self.users_repository.create_user(user_in, salt)

    #     self.sesion.add.assert_called_once()
    #     self.sesion.commit.assert_called_once()
    #     self.sesion.refresh.assert_called_once()

    #     self.assertEqual(created_user, user_out)

    @patch("libgravatar.Gravatar")
    async def test_create_user_success(self, mock_gravatar):
        user_in = UserIn(
            username="testuser", email="test@example.com", password="Password1!"
        )
        salt = "somesalt"
        expected = UserOut(
            id=1,
            username="testuser",
            email="test@example.com",
            password="Password1!",
            salt="somesalt",
            created_at=datetime.now(),
            avatar="Avatar",
        )

        mock_gravatar.return_value.get_image.return_value = "Avatar"

        actual = await self.users_repository.create_user(user_in, salt)

        self.assertEqual(expected.username, actual.username)
        self.assertEqual(expected.email, actual.email)
        self.assertEqual(expected.password, actual.password)
        self.assertEqual(expected.salt, actual.salt)
        self.assertEqual(expected.avatar, actual.avatar)

    async def test_create_user_gravatar_exception(self):
        user_in = UserIn(
            username="testuser", email="test@example.com", password="Password1!"
        )
        salt = "somesalt"

        mock_gravatar = patch("libgravatar.Gravatar")
        mock_gravatar.side_effect = Exception("Gravatar error")

        with self.assertRaises(Exception):
            await self.users_repository.create_user(user_in, salt)


if __name__ == "__main__":
    unittest.main()
