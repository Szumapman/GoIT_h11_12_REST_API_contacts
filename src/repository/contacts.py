from datetime import datetime, timedelta

from fastapi import HTTPException, status

from src.repository.abstract_repository import AbstractContactsRepository
from src.database.models import Contact
from src.schemas import ContactOut, ContactIn


class PostgresContactRepository(AbstractContactsRepository):
    def __init__(self, session):
        self._session = session

    async def get_contacts(
        self, search_name: str, search_email: str, upcoming_birthdays: bool
    ) -> list[ContactOut]:
        if (
            sum(
                param is not None
                for param in [search_name, search_email, upcoming_birthdays]
            )
            > 1
        ):
            raise HTTPException(
                status_code=400,
                detail="You can only search by one parameter at a time.",
            )
        if search_name:
            contacts = (
                self._session.query(Contact)
                .filter(
                    Contact.first_name.ilike(f"%{search_name}%")
                    | Contact.last_name.ilike(f"%{search_name}%")
                )
                .all()
            )
        elif search_email:
            contacts = (
                self._session.query(Contact)
                .filter(Contact.email.ilike(f"%{search_email}%"))
                .all()
            )
        elif upcoming_birthdays:
            today = datetime.now().date()
            next_week = today + timedelta(days=7)
            contacts_to_check = self._session.query(Contact).all()
            contacts = []
            for contact in contacts_to_check:
                if (
                    today
                    <= contact.birth_date.replace(year=today.year).date()
                    <= next_week
                ):
                    contacts.append(contact)
        else:
            contacts = self._session.query(Contact).all()
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

    async def get_contact(self, contact_id: int) -> ContactOut:
        contact = self._session.query(Contact).filter(Contact.id == contact_id).first()
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

    async def create_contact(self, contact: ContactIn) -> ContactOut:
        contact = Contact(
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
            birth_date=contact.birth_date,
            additional_info=contact.additional_info,
        )
        self._session.add(contact)
        self._session.commit()
        self._session.refresh(contact)
        return ContactOut(
            id=contact.id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
            birth_date=contact.birth_date,
            additional_info=contact.additional_info,
        )

    async def update_contact(self, contact_id: int, contact: ContactIn) -> ContactOut:
        changed_contact = (
            self._session.query(Contact).filter(Contact.id == contact_id).first()
        )
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
        self._session.commit()
        self._session.refresh(changed_contact)
        return ContactOut(
            id=changed_contact.id,
            first_name=changed_contact.first_name,
            last_name=changed_contact.last_name,
            email=changed_contact.email,
            phone=changed_contact.phone,
            birth_date=changed_contact.birth_date,
            additional_info=changed_contact.additional_info,
        )

    async def delete_contact(self, contact_id: int) -> ContactOut:
        contact = self._session.query(Contact).filter(Contact.id == contact_id).first()
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
            )
        self._session.delete(contact)
        self._session.commit()
        return ContactOut(
            id=contact.id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
            birth_date=contact.birth_date,
            additional_info=contact.additional_info,
        )
