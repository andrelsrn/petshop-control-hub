from pydantic import BaseModel
from datetime import datetime


class Sale(BaseModel):
    '''
    Representa o schema de uma venda para validação de dados na API.
    Usado ao criar uma nova venda via endpoint.
    '''
    product_id: str
    quantity: int
    total_value: float
    customer_id: str


class Booking(BaseModel):
    '''
    Representa o schema de um agendamento para validação de dados na API.
    Usado ao criar um novo agendamento via endpoint.
    '''
    service_name: str
    pet_id: str
    scheduled_time: datetime
    employee_id: str
    delivery: bool


class Customer(BaseModel):
    """
    Representa o schema de um cliente para validação de dados na API.
    Usado ao criar um novo cliente via endpoint.
    """
    name: str
    phone: str
    address: str
    pet_name: str
    pet_breed: str


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

