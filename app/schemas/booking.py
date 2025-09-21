from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PetResponse(BaseModel):
    id: int
    name: str
    breed: str

    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    id: int
    name: str
    job_title: str

    class Config:
        from_attributes = True

class Booking(BaseModel):
    '''
    Representa o schema de um agendamento para validação de dados na API.
    Usado ao criar um novo agendamento via endpoint.
    '''
    service_name: str
    pet_id: int
    scheduled_time: datetime
    employee_id: int
    delivery: bool


class BookingResponse(BaseModel):
    id: int
    service_name: str
    scheduled_time: datetime
    employee: EmployeeResponse
    pet: PetResponse

    class Config:
        from_attributes = True

class CustomerSearchResult(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class BookingUpdate(BaseModel):
    service_name: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    delivery: Optional[bool] = None
    pet_id: Optional[int] = None
    employee_id: Optional[int] = None

    class Config:
        from_attributes = True

