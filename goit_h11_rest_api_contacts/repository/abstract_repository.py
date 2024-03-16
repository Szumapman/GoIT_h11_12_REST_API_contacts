import abc

from goit_h11_rest_api_contacts.schemas import ContactIn, ContactOut


class AbstractContactsRepository(abc.ABC):
    @abc.abstractmethod
    async def get_contacts(
        self,
        search_name: str,
        search_email: str,
        upcoming_birthdays: bool,
    ) -> list[ContactOut]:
        pass

    @abc.abstractmethod
    async def get_contact(self, contact_id: int) -> ContactOut:
        pass

    @abc.abstractmethod
    async def create_contact(self, contact: ContactIn) -> ContactOut:
        pass

    @abc.abstractmethod
    async def update_contact(self, contact_id: int, contact: ContactIn) -> ContactOut:
        pass

    @abc.abstractmethod
    async def delete_contact(self, contact_id: int) -> ContactOut:
        pass
