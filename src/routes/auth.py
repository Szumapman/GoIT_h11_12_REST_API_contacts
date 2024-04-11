from fastapi import (
    APIRouter,
    HTTPException,
    Security,
    Depends,
    status,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi_limiter.depends import RateLimiter

from src.schemas import UserIn, UserCreated, TokenModel, RequestEmail
from src.repository.abstract_repository import AbstractUsersRepository
from src.database.dependencies import get_user_repository
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup",
    response_model=UserCreated,
    status_code=status.HTTP_201_CREATED,
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def signup(
    body: UserIn,
    background_tasks: BackgroundTasks,
    request: Request,
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
):
    """
    Handles the signup process for new users.

    Args:
        body (UserIn): The user data to create a new user.
        background_tasks (BackgroundTasks): Used to send the confirmation email in the background.
        request (Request): The current HTTP request.
        user_repo (AbstractUsersRepository): The repository to interact with the user data.

    Raises:
        HTTPException: If a user with the provided email already exists.

    Returns:
        UserCreated: The created user data.
    """
    if await user_repo.get_user_by_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {body.email} already exists",
        )
    body.password, salt = auth_service.get_password_hash(body.password)
    user = await user_repo.create_user(body, salt)
    request_type = "Confirmation email"
    background_tasks.add_task(
        send_email, user.email, user.username, request_type, request.base_url
    )
    return {"user": user, "detail": "User successfully created"}


@router.post(
    "/login",
    response_model=TokenModel,
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
):
    """
    Handles the login process for existing users.

    Args:
        body (OAuth2PasswordRequestForm): The user credentials to authenticate the user.
        user_repo (AbstractUsersRepository): The repository to interact with the user data.

    Raises:
        HTTPException: If the user email or password is incorrect, or if the user's email is not confirmed.

    Returns:
        TokenModel: The access and refresh tokens for the authenticated user.
    """
    user = await user_repo.get_user_by_email(body.username)
    # because of security reasons we don't want to tell the user if the email or password is incorrect
    if not user:
        # incorrect email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed",
        )
    if not auth_service.verify_password(body.password, user.password, user.salt):
        # incorrect password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await user_repo.update_token(user, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get(
    "/refresh_token",
    response_model=TokenModel,
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
):
    """
    Handles the refresh token process for authenticated users.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials containing the refresh token.
        user_repo (AbstractUsersRepository): The repository to interact with the user data.

    Raises:
        HTTPException: If the refresh token is invalid or does not match the user's stored refresh token.

    Returns:
        TokenModel: The new access and refresh tokens for the authenticated user.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await user_repo.get_user_by_email(email)
    if user.refresh_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await user_repo.update_token(user, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get(
    "/confirmed_email/{token}",
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def confirm_email(
    token: str, user_repo: AbstractUsersRepository = Depends(get_user_repository)
):
    """
    Handles the email confirmation process for a user.

    Args:
        token (str): The email confirmation token.
        user_repo (AbstractUsersRepository): The repository to interact with the user data.

    Raises:
        HTTPException: If the user does not exist or the email is already confirmed.

    Returns:
        dict: A message indicating that the email has been confirmed.
    """
    email = await auth_service.get_email_from_token(token)
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already confirmed"
        )
    await user_repo.confirm_email(email)
    return {"message": "Email confirmed"}


@router.post(
    "/request_email",
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
) -> dict:
    """
    Handles the request for a user to receive an email confirmation.

    Args:
        body (RequestEmail): The request body containing the user's email.
        background_tasks (BackgroundTasks): The background task scheduler to send the email.
        request (Request): The current HTTP request.
        user_repo (AbstractUsersRepository): The repository to interact with the user data.

    Raises:
        HTTPException: If the user's email is already confirmed.

    Returns:
        dict: A message indicating that an email has been sent if the email was in the database.
    """
    user = await user_repo.get_user_by_email(body.email)
    if user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already confirmed"
        )
    if user:
        request_type = "Confirmation email"
        background_tasks.add_task(
            send_email, user.email, user.username, request_type, request.base_url
        )
    return {
        "message": "If the email address was in our database, we sent an email with a confirmation link."
    }


@router.post(
    "/password-reset",
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def request_password_reset(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
) -> dict:
    """
    Handles the request to reset a user's password.

    Args:
        body (RequestEmail): The request body containing the user's email.
        background_tasks (BackgroundTasks): The background task scheduler to send the email.
        request (Request): The current HTTP request.
        user_repo (AbstractUsersRepository): The repository to interact with the user data.

    Raises:
        HTTPException: If the user's email is not found or not confirmed.

    Returns:
        dict: A message indicating that an email has been sent if the email was in the database and confirmed.
    """
    user = await user_repo.get_user_by_email(body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email not found"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email not confirmed"
        )
    if user:
        request_type = "Reset password"
        background_tasks.add_task(
            send_email, user.email, user.username, request_type, request.base_url
        )
    return {
        "message": "If the email address was in our database, we sent an email with link to reset password"
    }


@router.post(
    "/password-reset/{token}",
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def reset_password(
    token: str,
    new_password: str,
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
) -> dict:
    """
    Resets a user's password using the provided token and new password.

    Args:
        token (str): The password reset token.
        new_password (str): The new password to set for the user.
        user_repo (AbstractUsersRepository): The repository to interact with the user data.

    Raises:
        HTTPException: If the verification token is invalid or the user is not found.

    Returns:
        dict: A message indicating that the password has been changed.
    """
    email = await auth_service.get_email_from_token(token)
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    password, salt = auth_service.get_password_hash(new_password)
    await user_repo.update_password(email, password, salt)
    return {"message": "Password changed"}
