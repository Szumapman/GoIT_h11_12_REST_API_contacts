from pydantic import BaseModel, Field, EmailStr
from datetime import date

class ContactIn(BaseModel):
    firstname: str = Field(max_length=150)
    lastname: str = Field(max_length=150)
    email: EmailStr = Field(max_length=50, unique=True)
    phone: str = Field(max_length=50, unique=True)
    birth_date: date
    additional_info: str | None = Field(max_length=1000)
  
  
class ContactOut(ContactIn):
    id: int
    