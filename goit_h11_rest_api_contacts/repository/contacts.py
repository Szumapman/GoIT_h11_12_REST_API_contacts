from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from goit_h11_rest_api_contacts.database.models import Contact
from goit_h11_rest_api_contacts.schemas import ContactOut, ContactIn


async def get_contacts(db: Session) -> list[ContactOut]:
    contacts = db.query(Contact).all()
    return [
        ContactOut(
            id=contact.id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
            birth_date=contact.birth_date,
            additional_info=contact.additional_info,
        )
        for contact in contacts
    ]


async def get_contact(contact_id: int, db: Session) -> ContactOut:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return ContactOut(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        birth_date=contact.birth_date,
        additional_info=contact.additional_info,
    )


async def create_contact(contact: ContactIn, db: Session) -> ContactOut:
    contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        birth_date=contact.birth_date,
        additional_info=contact.additional_info,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return ContactOut(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        birth_date=contact.birth_date,
        additional_info=contact.additional_info,
    )


async def update_contact(
    contact_id: int, contact: ContactIn, db: Session
) -> ContactOut:
    changed_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if changed_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    changed_contact.first_name = contact.first_name
    changed_contact.last_name = contact.last_name
    changed_contact.email = contact.email
    changed_contact.phone = contact.phone
    changed_contact.birth_date = contact.birth_date
    changed_contact.additional_info = contact.additional_info
    db.commit()
    db.refresh(changed_contact)
    return ContactOut(
        id=changed_contact.id,
        first_name=changed_contact.first_name,
        last_name=changed_contact.last_name,
        email=changed_contact.email,
        phone=changed_contact.phone,
        birth_date=changed_contact.birth_date,
        additional_info=changed_contact.additional_info,
    )


async def delete_contact(contact_id: int, db: Session) -> ContactOut:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    db.delete(contact)
    db.commit()
    return ContactOut(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        birth_date=contact.birth_date,
        additional_info=contact.additional_info,
    )
