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

from src.schemas import UserIn, UserCreated, TokenModel
from src.repository.abstract_repository import AbstractUsersRepository
from src.database.dependencies import get_user_repository
from src.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserIn,
    background_tasks: BackgroundTasks,
    request: Request,
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
):
    if await user_repo.get_user_by_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email:{body.email} already exists",
        )
    body.password, salt = auth_service.get_password_hash(body.password)
    user = await user_repo.create_user(body, salt)
    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"user": user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
):
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


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
):
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
