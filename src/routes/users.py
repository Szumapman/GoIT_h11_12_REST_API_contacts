from fastapi import APIRouter, Depends, UploadFile, File
import cloudinary
import cloudinary.uploader

from src.database.dependencies import get_user_repository
from src.database.models import User
from src.repository.abstract_repository import AbstractUsersRepository
from src.schemas import UserOut
from src.services.auth import auth_service
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserOut)
async def read_current_user(
    current_user: UserOut = Depends(auth_service.get_current_user),
):
    return current_user


@router.patch("/me/avatar", response_model=UserOut)
async def update_user_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    user_repo: AbstractUsersRepository = Depends(get_user_repository),
):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    r = cloudinary.uploader.upload(
        file.file,
        public_id=f"Fastapi_Contact_App/{current_user.username}",
        overwrite=True,
    )
    src_url = cloudinary.CloudinaryImage(
        f"Fastapi_Contact_App/{current_user.username}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    user = await user_repo.update_avatar(current_user.email, src_url)
    return user
