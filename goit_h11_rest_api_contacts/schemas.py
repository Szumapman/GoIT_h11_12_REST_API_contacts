from typing import Dict

from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import date


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
