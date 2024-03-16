from typing import List
from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.orm import Session

from goit_h11_rest_api_contacts.database.db import get_db
from goit_h11_rest_api_contacts.schemas import ContactIn, ContactOut
from goit_h11_rest_api_contacts.repository import contacts as repository_contacts

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
    db: Session = Depends(get_db),
) -> List[ContactOut]:
    contacts = await repository_contacts.get_contacts(
        search_name, search_email, upcoming_birthdays, db
    )
    return contacts


@router.get("/{contact_id}")
async def read_contact(
    contact_id: int = Path(description="The ID of the contact to get", gt=0),
    db: Session = Depends(get_db),
) -> ContactOut:
    contact = await repository_contacts.get_contact(contact_id, db)
    return contact


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactIn, db: Session = Depends(get_db)
) -> ContactOut:
    return await repository_contacts.create_contact(contact, db)


@router.put("/{contact_id}")
async def update_contact(
    contact_id: int, contact: ContactIn, db: Session = Depends(get_db)
) -> ContactOut:
    return await repository_contacts.update_contact(contact_id, contact, db)


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)) -> ContactOut:
    return await repository_contacts.delete_contact(contact_id, db)
