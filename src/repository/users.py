from fastapi import HTTPException, status

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
        new_user = User(
            username=user.username,
            email=user.email,
            password=user.password,
            salt=salt,
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
        )

    async def update_token(self, user: UserOut, token: str | None) -> None:
        user.refresh_token = token
        self._session.commit()
