from typing import List
from fastapi import APIRouter, Depends, status, Query, Path

from src.auth import auth_service
from src.schemas import ContactIn, ContactOut, UserOut
from src.repository.abstract_repository import (
    AbstractContactsRepository,
)
from src.database.dependencies import get_contact_repository

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/")
async def read_contacts(
    search_name: None | str = Query(
        None, description="Search contacts by first or last name"
    ),
    search_email: None | str = Query(None, description="Search contacts by email"),
    upcoming_birthdays: None | bool = Query(
        None, description="Get contacts with birthdays in the next 7 days"
    ),
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> List[ContactOut]:
    contacts = await contact_repo.get_contacts(
        search_name, search_email, upcoming_birthdays, current_user
    )
    return contacts


@router.get("/{contact_id}")
async def read_contact(
    contact_id: int = Path(description="The ID of the contact to get", gt=0),
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> ContactOut:
    contact = await contact_repo.get_contact(contact_id, current_user)
    return contact


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactIn,
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> ContactOut:
    return await contact_repo.create_contact(contact, current_user)


@router.put("/{contact_id}")
async def update_contact(
    contact_id: int,
    contact: ContactIn,
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> ContactOut:
    return await contact_repo.update_contact(contact_id, contact, current_user)


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> ContactOut:
    return await contact_repo.delete_contact(contact_id, current_user)
