import re
from typing import Dict
from datetime import date, datetime

from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber


class ContactIn(BaseModel):
    first_name: str = Field(max_length=150)
    last_name: str = Field(max_length=150)
    email: EmailStr = Field(max_length=150, unique=True)
    phone: PhoneNumber = Field(max_length=50, unique=True)
    birth_date: date
    additional_info: Dict[str, str] | None = None

    PhoneNumber.default_region_code = "PL"
    PhoneNumber.phone_format = "E164"


class ContactOut(ContactIn):
    id: int = Field(default=1, ge=1)

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    username: str = Field(min_length=5, max_length=150, unique=True)
    email: EmailStr = Field(max_length=150, unique=True)
    password: str = Field(min_length=8, max_length=150)

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,150}$", password):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit and one special character"
            )
        return password


class UserOut(UserIn):
    id: int = Field(default=1, ge=1)
    created_at: datetime

    class Config:
        orm_mode = True


class UserCreated(BaseModel):
    user: UserOut
    detail: str = "User created successfully"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
