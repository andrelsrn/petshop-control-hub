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
