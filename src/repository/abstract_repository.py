import abc

from src.schemas import ContactIn, ContactOut, UserIn, UserOut


class AbstractContactsRepository(abc.ABC):
    """
    Defines an abstract base class for a contacts repository. This class provides the interface for managing contacts, including getting contacts, getting a specific contact, creating a new contact, updating an existing contact, and deleting a contact.

    The repository is responsible for interacting with the underlying data storage system to perform these operations. Concrete implementations of this abstract class will provide the actual implementation details.
    """

    @abc.abstractmethod
    async def get_contacts(
        self,
        search_name: str,
        search_email: str,
        upcoming_birthdays: bool,
        user: UserOut,
    ) -> list[ContactOut]:
        """
        Get a list of contacts that match the given search criteria and belong to the specified user.

        Args:
            search_name (str): The name to search for in the contacts.
            search_email (str): The email to search for in the contacts.
            upcoming_birthdays (bool): If True, only return contacts with upcoming birthdays.
            user (UserOut): The user whose contacts should be returned.

        Returns:
            list[ContactOut]: A list of contacts matching the search criteria and belonging to the specified user.
        """
        pass

    @abc.abstractmethod
    async def get_contact(
        self,
        contact_id: int,
        user: UserOut,
    ) -> ContactOut:
        """
        Get a specific contact belonging to the specified user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (UserOut): The user whose contact should be retrieved.

        Returns:
            ContactOut: The contact matching the provided ID and belonging to the specified user.
        """
        pass

    @abc.abstractmethod
    async def create_contact(self, contact: ContactIn, user: UserOut) -> ContactOut:
        """
        Create a new contact belonging to the specified user.

        Args:
            contact (ContactIn): The contact information to create.
            user (UserOut): The user for whom the contact should be created.

        Returns:
            ContactOut: The newly created contact.
        """
        pass

    @abc.abstractmethod
    async def update_contact(
        self, contact_id: int, contact: ContactIn, user: UserOut
    ) -> ContactOut:
        """
        Update a specific contact belonging to the specified user.

        Args:
            contact_id (int): The ID of the contact to update.
            contact (ContactIn): The updated contact information.
            user (UserOut): The user whose contact should be updated.

        Returns:
            ContactOut: The updated contact.
        """
        pass

    @abc.abstractmethod
    async def delete_contact(self, contact_id: int, user: UserOut) -> ContactOut:
        """
        Delete a specific contact belonging to the specified user.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (UserOut): The user whose contact should be deleted.

        Returns:
            ContactOut: The deleted contact.
        """
        pass


class AbstractUsersRepository(abc.ABC):
    """
    Defines an abstract base class for a users repository. This class provides the interface for managing users, including getting a user by email, creating a new user, updating a user's token, confirming a user's email, updating a user's avatar, and updating a user's password.

    The repository is responsible for interacting with the underlying data storage system to perform these operations. Concrete implementations of this abstract class will provide the actual implementation details.
    """

    @abc.abstractmethod
    async def get_user_by_email(self, email: str) -> UserOut:
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            UserOut: The user with the specified email address.
        """
        pass

    @abc.abstractmethod
    async def create_user(self, user: UserIn, salt: str) -> UserOut:
        """
        Creates a new user with the provided user data and salt.

        Args:
            user (UserIn): The user data to create the new user with.
            salt (str): The salt to use when hashing the user's password.

        Returns:
            UserOut: The newly created user.
        """
        pass

    @abc.abstractmethod
    async def update_token(self, user: UserOut, token: str | None) -> None:
        """
        Updates the token for the specified user.

        Args:
            user (UserOut): The user whose token should be updated.
            token (str | None): The new token to set for the user, or `None` to clear the token.

        Returns:
            None
        """
        pass

    @abc.abstractmethod
    async def confirm_email(self, email: str) -> None:
        """
        Confirms the email address for the specified user.

        Args:
            email (str): The email address of the user to confirm.

        Returns:
            None
        """
        pass

    @abc.abstractmethod
    async def update_avatar(self, email: str, avatar_url: str) -> UserOut:
        """
        Updates the avatar for the specified user.

        Args:
            email (str): The email address of the user whose avatar should be updated.
            avatar_url (str): The URL of the new avatar image to set for the user.

        Returns:
            UserOut: The updated user object with the new avatar.
        """
        pass

    @abc.abstractmethod
    async def update_password(self, email: str, password: str, salt: str) -> UserOut:
        """
        Updates the password for the specified user.

        Args:
            email (str): The email address of the user whose password should be updated.
            password (str): The new password to set for the user.
            salt (str): The salt to use when hashing the new password.

        Returns:
            UserOut: The updated user object with the new password.
        """
        pass
