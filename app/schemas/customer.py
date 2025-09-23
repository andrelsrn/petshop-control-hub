from pydantic import BaseModel, validator
from datetime import datetime
from validate_docbr import CPF
import re
from typing import Optional


def normalize_text(text: str) -> str:
    '''Remove todos os caracteres não alfanuméricos de um texto.'''
    if not text:
        return ""
    return re.sub(r'\D', '', text)



class CustomerIn(BaseModel):
    """
    Representa o schema de um cliente para validação de dados na API.
    Usado ao criar um novo cliente via endpoint.
    """
    name: str
    phone: str
    address: str
    cpf: str

    @validator('cpf')
    def validate_and_normalize_cpf(cls, v):
        '''Valida o CPF e o retorna normalizado.'''
        normalized_cpf = normalize_cpf(v)

        cpf_validator = CPF()
        if not cpf_validator.validate(normalized_cpf):
            raise ValueError('CPF inválido')

        return normalized_cpf

    @validator('phone')
    def validate_and_normalize_phone(cls, v):
        '''Valida o número de telefone e o retorna normalizado.'''
        normalized_phone = normalize_text(v)

        if not normalized_phone or len(normalized_phone) < 10:
            raise ValueError('Número de telefone inválido')

        return normalized_phone






def normalize_cpf(cpf: str) -> str:
    '''Remove todos os caracteres não numéricos de um CPF.'''
    if not cpf:
        return ""
    return re.sub(r'\D', '', cpf)


class Customer(CustomerIn):
    """
    Schema para retornar um cliente, incluindo o id.
    """
    id: int

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

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    cpf: Optional[str] = None

    class Config:
        from_attributes = True