import secrets
import pickle
from datetime import datetime, timedelta

import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from src.database.dependencies import get_user_repository
from src.repository.abstract_repository import AbstractUsersRepository
from src.schemas import UserOut
from src.conf.config import settings


class Auth:
    """
    The `Auth` class provides authentication-related functionality for the application, including password hashing, token generation, and user retrieval.

    The class has the following methods:

    - `verify_password`: Verifies a plain-text password against a hashed password and salt.
    - `get_password_hash`: Generates a hashed password and salt.
    - `_create_token`: A generic function to create a JWT token with a specified expiration time and scope.
    - `create_access_token`: Creates an access token with a 15-minute expiration.
    - `create_refresh_token`: Creates a refresh token with a 7-day expiration.
    - `decode_refresh_token`: Decodes a refresh token and returns the associated email.
    - `get_current_user`: Retrieves the current user from the request token, caching the user in Redis if necessary.
    - `create_email_token`: Creates a token for email verification with a 1-day expiration.
    - `get_email_from_token`: Decodes an email verification token and returns the associated email.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    SALT_LENGTH = settings.salt_length
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis_base = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def __init__(self, user_repository: AbstractUsersRepository) -> None:
        """
        Initializes the `Auth` class with the provided `user_repository` instance.

        Args:
            user_repository (AbstractUsersRepository): The repository for managing user-related operations.
        """
        self._user_repository = user_repository

    def verify_password(
        self, plain_password: str, hashed_password: str, salt: str
    ) -> bool:
        """
        Verifies a plain-text password against a hashed password and salt.

        Args:
            plain_password (str): The plain-text password to verify.
            hashed_password (str): The hashed password to compare against.
            salt (str): The salt used to hash the original password.

        Returns:
            bool: True if the plain-text password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password + salt, hashed_password)

    def get_password_hash(self, password: str) -> (str, str):
        """
        Generates a hashed password and salt.

        Args:
            password (str): The plain-text password to hash.

        Returns:
            Tuple[str, str]: A tuple containing the hashed password and the generated salt.
        """
        salt = secrets.token_hex(self.SALT_LENGTH)
        password = self.pwd_context.hash(password + salt)
        return password, salt

    # generic function to generate a token
    async def _create_token(
        self, data: dict, expires_delta: timedelta, scope: str
    ) -> str:
        """
        Generates a JWT token with the provided data, expiration time, and scope.

        Args:
            data (dict): A dictionary containing the data to be encoded in the token.
            expires_delta (timedelta): The time delta after which the token will expire.
            scope (str): The scope associated with the token.

        Returns:
            str: The encoded JWT token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": scope})
        encoded_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_token

    async def create_access_token(
        self, data: dict, expires_delta: timedelta = None
    ) -> str:
        """
        Generates an access token with the provided data and an expiration time.

        Args:
            data (dict): A dictionary containing the data to be encoded in the token.
            expires_delta (timedelta, optional): The time delta after which the token will expire. Defaults to 15 minutes.

        Returns:
            str: The encoded JWT access token.
        """
        if not expires_delta:
            expires_delta = timedelta(minutes=15)
        return await self._create_token(data, expires_delta, "access_token")

    async def create_refresh_token(
        self, data: dict, expires_delta: timedelta = None
    ) -> str:
        """
        Generates a refresh token with the provided data and an expiration time.

        Args:
            data (dict): A dictionary containing the data to be encoded in the token.
            expires_delta (timedelta, optional): The time delta after which the token will expire. Defaults to 7 days.

        Returns:
            str: The encoded JWT refresh token.
        """
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
        """
        Retrieves the current user based on the provided access token.

        Args:
            token (str): The access token to be used for authentication.

        Returns:
            UserOut: The authenticated user.

        Raises:
            HTTPException: If the token is invalid or the user cannot be found.
        """
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
        """
        Creates an email token with an expiration date.

        Args:
            data (dict): A dictionary containing the data to be encoded in the token.

        Returns:
            Tuple[str, str]: The generated token and the expiration date as a string in the format "dd-mm-YYYY HH:MM".
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token, expire.strftime("%d-%m-%Y %H:%M")

    async def get_email_from_token(self, token: str) -> str:
        """
        Extracts the email from a given JWT token.

        Args:
            token (str): The JWT token to extract the email from.

        Returns:
            str: The email extracted from the token.

        Raises:
            HTTPException: If the token is invalid or the email cannot be extracted.
        """
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
