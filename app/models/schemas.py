from pydantic import BaseModel
from datetime import datetime


class Sale(BaseModel):
    '''
    Representa o schema de uma venda para validação de dados na API.
    Usado ao criar uma nova venda via endpoint.
    '''
    product_name: str
    quantity: int
    total_value: float
    customer_id: int


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


class CustomerIn(BaseModel):
    """
    Representa o schema de um cliente para validação de dados na API.
    Usado ao criar um novo cliente via endpoint.
    """
    name: str
    phone: str
    address: str



class Customer(CustomerIn):
    """
    Schema para retornar um cliente, incluindo o id.
    """
    id: int

    class Config:
        from_attributes = True


class EmployeeIn(BaseModel):
    '''Representa o schema de um funcionário para validação de dados na API.
    Usado ao criar um novo funcionário via endpoint.
    '''
    name: str
    job_title: str
    phone: str


class Employee(EmployeeIn):
    '''Schema para retornar um funcionário, incluindo o id.
    '''
    id: int

    class Config:
        from_attributes = True


class KPIs(BaseModel):
    '''Modelo para os dados do dashboard.'''
    total_revenue: float
    total_sales: int
    total_bookings: int
    total_customers: int


class InventoryIn(BaseModel):
    '''Representa o schema de um produto no inventário para validação de dados na API.
    '''
    product_name: str  # tirei o id
    quantity: int
    price: float
    low_stock_threshold: int


class Inventory(InventoryIn):
    '''Schema para retornar um  produto do inventário, incluindo o id.
    '''
    id: int

    class Config:
        orm_mode = True


class PetIn(BaseModel):
    name: str
    breed: str
    date_of_birth: datetime
    customer_id: int


class Pet(PetIn):
    id: int

    class Config:
        orm_mode = True


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


class BookingResponse(BaseModel):
    id: int
    service_name: str
    scheduled_time: datetime
    employee: EmployeeResponse
    pet: PetResponse

    class Config:
        from_attributes = True
