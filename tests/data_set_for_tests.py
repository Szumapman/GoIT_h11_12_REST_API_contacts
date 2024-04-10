from datetime import datetime, date

from src.database.models import Contact
from src.schemas import ContactOut, ContactIn, UserOut, UserIn


# user
_id = 1
_username = "testuser"
_password = "Pass123!"
_user_email = "test@example.com"
_salt = "somesalt"
_created_at_set = datetime.now()
_avatar = "Avatar_url"

# contact 1
_contact_id = 1
_first_name = "firstname"
_last_name = "lastname"
_email = "contact@example.com"
_phone = "+48654789654"
_birth_date = datetime(2000, 4, 12)

# contact 2
_contact_2_id = 2
_first_name_2 = "firstname_2"
_last_name_2 = "lastname_2"
_email_2 = "contact_2@example.com"
_phone_2 = "+48654789655"
_birth_date_2 = datetime(1988, 4, 16)

user_out = UserOut(
    id=_id,
    username=_username,
    email=_user_email,
    password=_password,
    salt=_salt,
    created_at=_created_at_set,
    avatar=_avatar,
)

contact = Contact(
    id=_contact_id,
    first_name=_first_name,
    last_name=_last_name,
    email=_email,
    phone=_phone,
    birth_date=_birth_date,
    user_id=_id,
)

contact_in = ContactIn(
    first_name=_first_name,
    last_name=_last_name,
    email=_email,
    phone=_phone,
    birth_date=_birth_date,
)

contact_out = ContactOut(
    id=_contact_id,
    first_name=_first_name,
    last_name=_last_name,
    email=_email,
    phone=_phone,
    birth_date=_birth_date,
    user_id=_id,
)

contact_2 = Contact(
    id=_contact_2_id,
    first_name=_first_name_2,
    last_name=_last_name_2,
    email=_email_2,
    phone=_phone_2,
    birth_date=_birth_date_2,
    user_id=_id,
)

contact_out_2 = ContactOut(
    id=_contact_2_id,
    first_name=_first_name_2,
    last_name=_last_name_2,
    email=_email_2,
    phone=_phone_2,
    birth_date=_birth_date_2,
    user_id=_id,
)

get_contacts_success_test_cases = [
    {"search_name": None, "search_email": None, "upcoming_birthdays": None},
    {
        "search_name": "testname",
        "search_email": None,
        "upcoming_birthdays": None,
    },
    {
        "search_name": None,
        "search_email": "test@example.com",
        "upcoming_birthdays": None,
    },
    {"search_name": None, "search_email": None, "upcoming_birthdays": True},
]

get_contacts_exception_too_many_arguments_test_cases = [
    {
        "search_name": "testname",
        "search_email": "test@example.com",
        "upcoming_birthdays": None,
    },
    {
        "search_name": None,
        "search_email": "test@example.com",
        "upcoming_birthdays": True,
    },
    {
        "search_name": "testname",
        "search_email": None,
        "upcoming_birthdays": True,
    },
    {
        "search_name": "testname",
        "search_email": "test@example.com",
        "upcoming_birthdays": True,
    },
]
