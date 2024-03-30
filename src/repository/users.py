from fastapi import HTTPException, status
from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.repository.abstract_repository import AbstractUsersRepository
from src.schemas import UserOut, UserIn
from src.database.models import User


class PostgresUserRepository(AbstractUsersRepository):
    def __init__(self, session):
        self._session = session

    async def get_user_by_email(self, email: str) -> UserOut | None:
        user = self._session.query(User).filter(User.email == email).first()
        return user

    async def create_user(self, user: UserIn, salt: str) -> UserOut:
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
        user.refresh_token = token
        self._session.commit()

    async def confirm_email(self, email: str) -> None:
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email:{email} not found",
            )
        user.confirmed = True
        self._session.commit()

    async def update_avatar(self, email: str, avatar_url: str) -> UserOut:
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
