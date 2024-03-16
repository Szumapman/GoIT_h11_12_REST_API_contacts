from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from goit_h11_rest_api_contacts.database.db import get_db
from goit_h11_rest_api_contacts.schemas import ContactIn, ContactOut
from goit_h11_rest_api_contacts.repository import contacts as repository_contacts

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactOut])
async def read_contacts(db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(db)
    return contacts


@router.get("/{contact_id}", response_model=ContactOut)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
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
