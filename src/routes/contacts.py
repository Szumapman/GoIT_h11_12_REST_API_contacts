from typing import List
from fastapi import APIRouter, Depends, status, Query, Path
from fastapi_limiter.depends import RateLimiter

from src.services.auth import auth_service
from src.schemas import ContactIn, ContactOut, UserOut
from src.repository.abstract_repository import (
    AbstractContactsRepository,
)
from src.database.dependencies import get_contact_repository

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
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
    """
    Retrieves a list of contacts based on the provided search criteria.

    Args:
        search_name (str, optional): Search contacts by first or last name.
        search_email (str, optional): Search contacts by email.
        upcoming_birthdays (bool, optional): Get contacts with birthdays in the next 7 days.
        current_user (UserOut): The current authenticated user.
        contact_repo (AbstractContactsRepository): The contacts repository.

    Returns:
        List[ContactOut]: A list of contacts matching the search criteria.
    """
    contacts = await contact_repo.get_contacts(
        search_name, search_email, upcoming_birthdays, current_user
    )
    return contacts


@router.get(
    "/{contact_id}",
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def read_contact(
    contact_id: int = Path(description="The ID of the contact to get", gt=0),
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> ContactOut:
    """
    Retrieves a single contact by its ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        current_user (UserOut): The current authenticated user.
        contact_repo (AbstractContactsRepository): The contacts repository.

    Returns:
        ContactOut: The contact matching the provided ID.
    """
    contact = await contact_repo.get_contact(contact_id, current_user)
    return contact


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def create_contact(
    contact: ContactIn,
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> ContactOut:
    """
    Creates a new contact for the current authenticated user.

    Args:
        contact (ContactIn): The contact information to create.
        current_user (UserOut): The current authenticated user.
        contact_repo (AbstractContactsRepository): The contacts repository.

    Returns:
        ContactOut: The newly created contact.
    """
    return await contact_repo.create_contact(contact, current_user)


@router.put(
    "/{contact_id}",
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def update_contact(
    contact_id: int,
    contact: ContactIn,
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> ContactOut:
    """
    Updates an existing contact for the current authenticated user.

    Args:
        contact_id (int): The ID of the contact to update.
        contact (ContactIn): The updated contact information.
        current_user (UserOut): The current authenticated user.
        contact_repo (AbstractContactsRepository): The contacts repository.

    Returns:
        ContactOut: The updated contact.
    """
    return await contact_repo.update_contact(contact_id, contact, current_user)


@router.delete(
    "/{contact_id}",
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def delete_contact(
    contact_id: int,
    current_user: UserOut = Depends(auth_service.get_current_user),
    contact_repo: AbstractContactsRepository = Depends(get_contact_repository),
) -> ContactOut:
    """
    Deletes an existing contact for the current authenticated user.

    Args:
        contact_id (int): The ID of the contact to delete.
        current_user (UserOut): The current authenticated user.
        contact_repo (AbstractContactsRepository): The contacts repository.

    Returns:
        ContactOut: The deleted contact.
    """
    return await contact_repo.delete_contact(contact_id, current_user)
