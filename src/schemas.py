import re
from typing import Dict
from datetime import date, datetime

from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber


class ContactIn(BaseModel):
    """
    Defines the input schema for a contact.

    The `ContactIn` model represents the input data for creating a new contact. It includes fields for the contact's first name, last name, email, phone number, birth date, and optional additional information.

    The `PhoneNumber` field is configured to use the "PL" (Poland) region code and the "E164" phone number format.
    """

    first_name: str = Field(max_length=150)
    last_name: str = Field(max_length=150)
    email: EmailStr = Field(max_length=150, unique=True)
    phone: PhoneNumber = Field(max_length=50, unique=True)
    birth_date: date
    additional_info: Dict[str, str] | None = None

    PhoneNumber.default_region_code = "PL"
    PhoneNumber.phone_format = "E164"


class ContactOut(ContactIn):
    """
    Defines the output schema for a contact.

    The `ContactOut` model inherits from the `ContactIn` model and adds an `id` field. This model represents the output data for a contact, including the unique identifier.

    The `id` field is configured to have a default value of 1 and a minimum value of 1.

    The `Config` class is used to configure the model, in this case, to generate the model from the class attributes.
    """

    id: int = Field(default=1, ge=1)

    class Config:
        from_attributes = True


class UserIn(BaseModel):
    """
    Defines the input schema for a user.

    The `UserIn` model represents the input data for creating a new user. It includes fields for the user's username, email, and password.

    The `username` field is configured to have a minimum length of 5 characters and a maximum length of 150 characters, and to be unique.
    The `email` field is configured to be a valid email address and to be unique.
    The `password` field is configured to have a minimum length of 8 characters and a maximum length of 150 characters, and to contain at least one uppercase letter, one lowercase letter, one digit, and one special character.

    The `validate_password` function is a field validator that enforces the password requirements.
    """

    username: str = Field(min_length=5, max_length=150, unique=True)
    email: EmailStr = Field(max_length=150, unique=True)
    password: str = Field(min_length=8, max_length=150)

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        elif len(password) > 75:
            raise ValueError("Password must be at most 75 characters long")
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,75}$", password):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit and one special character"
            )
        return password


class UserOut(UserIn):
    """
    Defines the output schema for a user.

    The `UserOut` model inherits from the `UserIn` model and adds additional fields for the user's unique identifier (`id`), salt, creation timestamp (`created_at`), and avatar.

    The `id` field is configured to have a default value of 1 and a minimum value of 1.

    The `Config` class is used to configure the model, in this case, to generate the model from the class attributes.
    """

    id: int = Field(default=1, ge=1)
    salt: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserCreated(BaseModel):
    """
    Defines the output schema for a newly created user.

    The `UserCreated` model contains two fields:
    - `user`: an instance of the `UserOut` model, representing the newly created user.
    - `detail`: a string indicating that the user was created successfully.
    """

    user: UserOut
    detail: str = "User created successfully"


class TokenModel(BaseModel):
    """
    Defines a model for an access and refresh token pair, along with the token type.

    The `TokenModel` contains the following fields:
    - `access_token`: The access token string.
    - `refresh_token`: The refresh token string.
    - `token_type`: The type of token, which is set to "bearer" by default.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Defines a model for a user's email address.

    The `RequestEmail` model contains a single field, `email`, which is an email address string.
    """

    email: EmailStr
