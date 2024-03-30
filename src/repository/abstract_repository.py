import abc

from src.schemas import ContactIn, ContactOut, UserIn, UserOut


class AbstractContactsRepository(abc.ABC):
    @abc.abstractmethod
    async def get_contacts(
        self,
        search_name: str,
        search_email: str,
        upcoming_birthdays: bool,
        user: UserOut,
    ) -> list[ContactOut]:
        pass

    @abc.abstractmethod
    async def get_contact(
        self,
        contact_id: int,
        user: UserOut,
    ) -> ContactOut:
        pass

    @abc.abstractmethod
    async def create_contact(self, contact: ContactIn, user: UserOut) -> ContactOut:
        pass

    @abc.abstractmethod
    async def update_contact(
        self, contact_id: int, contact: ContactIn, user: UserOut
    ) -> ContactOut:
        pass

    @abc.abstractmethod
    async def delete_contact(self, contact_id: int, user: UserOut) -> ContactOut:
        pass


class AbstractUsersRepository(abc.ABC):
    @abc.abstractmethod
    async def get_user_by_email(self, email: str) -> UserOut:
        pass

    @abc.abstractmethod
    async def create_user(self, user: UserIn, salt: str) -> UserOut:
        pass

    @abc.abstractmethod
    async def update_token(self, user: UserOut, token: str | None) -> None:
        pass

    @abc.abstractmethod
    async def confirm_email(self, email: str) -> None:
        pass

    @abc.abstractmethod
    async def update_avatar(self, email: str, avatar_url: str) -> UserOut:
        pass

    @abc.abstractmethod
    async def update_password(self, email: str, password: str, salt: str) -> UserOut:
        pass
