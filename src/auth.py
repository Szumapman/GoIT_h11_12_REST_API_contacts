import os
import secrets
import pickle
from dotenv import load_dotenv
from datetime import datetime, timedelta

import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from src.database.dependencies import get_user_repository
from src.repository.abstract_repository import AbstractUsersRepository
from src.schemas import UserOut


class Auth:
    load_dotenv()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    SALT_LENGTH = int(os.getenv("SALT_LENGTH"))
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
    redis_base = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db=0)

    def __init__(self, user_repository: AbstractUsersRepository) -> None:
        self._user_repository = user_repository

    def verify_password(
        self, plain_password: str, hashed_password: str, salt: str
    ) -> bool:
        return self.pwd_context.verify(plain_password + salt, hashed_password)

    def get_password_hash(self, password: str) -> (str, str):
        salt = secrets.token_hex(self.SALT_LENGTH)
        password = self.pwd_context.hash(password + salt)
        return password, salt

    # generic function to generate a token
    async def _create_token(
        self, data: dict, expires_delta: timedelta, scope: str
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": scope})
        encoded_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_token

    async def create_access_token(
        self, data: dict, expires_delta: timedelta = None
    ) -> str:
        if not expires_delta:
            expires_delta = timedelta(minutes=15)
        return await self._create_token(data, expires_delta, "access_token")

    async def create_refresh_token(
        self, data: dict, expires_delta: timedelta = None
    ) -> str:
        if not expires_delta:
            expires_delta = timedelta(days=7)
        return await self._create_token(data, expires_delta, "refresh_token")

    async def decode_refresh_token(self, refresh_token: str) -> str:
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> UserOut:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email: str = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = self.redis_base.get(f"user:{email}")
        if user is None:
            user = await self._user_repository.get_user_by_email(email)
            if user is None:
                raise credentials_exception
            self.redis_base.set(f"user:{email}", pickle.dumps(user))
            self.redis_base.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict) -> (str, str):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token, expire.strftime("%d-%m-%Y %H:%M")

    async def get_email_from_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth(get_user_repository())
