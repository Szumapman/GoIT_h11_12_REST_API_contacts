from fastapi import HTTPException, status
from libgravatar import Gravatar

from src.repository.abstract_repository import AbstractUsersRepository
from src.schemas import UserOut, UserIn
from src.database.models import User


class PostgresUserRepository(AbstractUsersRepository):
    """
    Concrete implementation of the Users repository.

    Args:
        AbstractUsersRepository (AbstractUsersRepository): Abstract base class for the Users repository.
    """

    def __init__(self, session):
        """
        Initialize the PostgresUserRepository with an active database session.

        Args:
            session (SessionLocal): session object for the database.
        """
        self._session = session

    async def get_user_by_email(self, email: str) -> UserOut | None:
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            UserOut | None: The user object if found, otherwise `None`.
        """
        user = self._session.query(User).filter(User.email == email).first()
        return user

    async def create_user(self, user: UserIn, salt: str) -> UserOut:
        """
        Creates a new user in the database.

        Args:
            user (UserIn): The user data to create the new user.
            salt (str): The salt to be used for hashing the user's password.

        Returns:
            UserOut: The created user object.
        """
        avatar = None
        try:
            gravatar = Gravatar(user.email)
            avatar = gravatar.get_image(size=256)
        except Exception as e:
            print(e)
        new_user = User(
            username=user.username,
            email=user.email,
            password=user.password,
            salt=salt,
            avatar=avatar,
        )
        self._session.add(new_user)
        self._session.commit()
        self._session.refresh(new_user)
        return UserOut(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            password=new_user.password,
            salt=new_user.salt,
            created_at=new_user.created_at,
            avatar=new_user.avatar,
        )

    async def update_token(self, user: UserOut, token: str | None) -> None:
        """
        Updates the refresh token for the given user.

        Args:
            user (UserOut): The user object to update the refresh token for.
            token (str | None): The new refresh token to set for the user, or `None` to clear the token.

        Returns:
            None
        """
        user.refresh_token = token
        self._session.commit()

    async def confirm_email(self, email: str) -> None:
        """
        Confirms the email address of the user with the given email.

        Args:
            email (str): The email address of the user to confirm.

        Raises:
            HTTPException: If the user with the given email is not found.

        Returns:
            None
        """
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email:{email} not found",
            )
        user.confirmed = True
        self._session.commit()

    async def update_avatar(self, email: str, avatar_url: str) -> UserOut:
        """
        Updates the avatar for the user with the given email address.

        Args:
            email (str): The email address of the user to update the avatar for.
            avatar_url (str): The URL of the new avatar image to set for the user.

        Raises:
            HTTPException: If the user with the given email is not found.

        Returns:
            UserOut: The updated user object with the new avatar.
        """
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email:{email} not found",
            )
        user.avatar = avatar_url
        self._session.commit()
        return UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            password=user.password,
            salt=user.salt,
            created_at=user.created_at,
            avatar=user.avatar,
        )

    async def update_password(self, email: str, password: str, salt: str) -> None:
        """
        Updates the password for the user with the given email address.

        Args:
            email (str): The email address of the user to update the password for.
            password (str): The new password to set for the user.
            salt (str): The new salt to set for the user.

        Raises:
            HTTPException: If the user with the given email is not found.

        Returns:
            None
        """
        user = await self.get_user_by_email(email)
        user.password = password
        user.salt = salt
        self._session.commit()
