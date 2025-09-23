from pydantic import BaseModel
from datetime import datetime


class PetIn(BaseModel):
    name: str
    name_tutor: str 
    breed: str
    species: str
    date_of_birth: datetime
    customer_id: int


class Pet(PetIn):
    id: int

    class Config:
        orm_mode = True

class PetUpdate(BaseModel):
    name: str | None = None
    name_tutor: str | None = None
    breed: str | None = None
    species: str | None = None
    date_of_birth: datetime | None = None
    customer_id: int | None = None

    class Config:
        from_attributes = True
