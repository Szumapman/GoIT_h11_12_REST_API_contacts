from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import and_

from src.repository.abstract_repository import AbstractContactsRepository
from src.database.models import Contact
from src.schemas import ContactOut, ContactIn, UserOut, UserIn


class PostgresContactRepository(AbstractContactsRepository):
    """
    Concrete implementation of the Contacts repository.

    Args:
        AbstractContactsRepository (AbstractContactsRepository): Abstract base class for the Contacts repository.
    """

    def __init__(self, session):
        """
        Initializes the PostgresContactRepository with the provided database session.

        Args:
            session (sqlalchemy.orm.Session): The database session to use for database operations.
        """

        self._session = session

    async def get_contacts(
        self,
        search_name: str,
        search_email: str,
        upcoming_birthdays: bool,
        user: UserOut,
    ) -> list[ContactOut]:
        """
        Retrieves a list of contacts based on the provided search parameters.

        Args:
            search_name (str): The name to search for in the contacts.
            search_email (str): The email to search for in the contacts.
            upcoming_birthdays (bool): Whether to retrieve contacts with upcoming birthdays.
            user (UserOut): The user whose contacts to retrieve.

        Returns:
            list[ContactOut]: A list of contacts matching the search parameters.

        Raises:
            HTTPException: If more than one search parameter is provided.
        """
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
                    and_(
                        Contact.user_id == user.id,
                        Contact.first_name.ilike(f"%{search_name}%")
                        | Contact.last_name.ilike(f"%{search_name}%"),
                    )
                )
                .all()
            )
        elif search_email:
            contacts = (
                self._session.query(Contact)
                .filter(
                    and_(
                        Contact.email.ilike(f"%{search_email}%"),
                        Contact.user_id == user.id,
                    )
                )
                .all()
            )
        elif upcoming_birthdays:
            today = datetime.now().date()
            next_week = today + timedelta(days=7)
            contacts_to_check = (
                self._session.query(Contact).filter(Contact.user_id == user.id).all()
            )
            contacts = []
            for contact in contacts_to_check:
                if (
                    today
                    <= contact.birth_date.replace(year=today.year).date()
                    <= next_week
                ):
                    contacts.append(contact)
        else:
            contacts = (
                self._session.query(Contact).filter(Contact.user_id == user.id).all()
            )
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

    async def get_contact(self, contact_id: int, user: UserOut) -> ContactOut:
        """
        Retrieves a contact by its ID for the specified user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (UserOut): The user for whom the contact should be retrieved.

        Returns:
            ContactOut: The contact with the specified ID for the given user.

        Raises:
            HTTPException: If the contact is not found.
        """
        contact = (
            self._session.query(Contact)
            .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
            .first()
        )
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
            user_id=user.id,
        )

    async def create_contact(self, contact: ContactIn, user: UserOut) -> ContactOut:
        """
        Creates a new contact for the specified user.

        Args:
            contact (ContactIn): The contact information to create.
            user (UserOut): The user for whom the contact should be created.

        Returns:
            ContactOut: The created contact.
        """
        contact = Contact(
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone=contact.phone,
            birth_date=contact.birth_date,
            additional_info=contact.additional_info,
            user_id=user.id,
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
            user_id=user.id,
        )

    async def update_contact(
        self, contact_id: int, contact: ContactIn, user: UserOut
    ) -> ContactOut:
        """
        Updates an existing contact for the specified user.

        Args:
            contact_id (int): The ID of the contact to update.
            contact (ContactIn): The updated contact information.
            user (UserOut): The user for whom the contact should be updated.

        Returns:
            ContactOut: The updated contact.

        Raises:
            HTTPException: If the contact is not found.
        """
        changed_contact = (
            self._session.query(Contact)
            .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
            .first()
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
            user_id=user.id,
        )

    async def delete_contact(self, contact_id: int, user: UserOut) -> ContactOut:
        """
        Deletes an existing contact for the specified user.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (UserOut): The user for whom the contact should be deleted.

        Returns:
            ContactOut: The deleted contact.

        Raises:
            HTTPException: If the contact is not found.
        """
        contact = (
            self._session.query(Contact)
            .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
            .first()
        )
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
            user_id=user.id,
        )
