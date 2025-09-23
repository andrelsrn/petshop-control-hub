from pydantic import BaseModel, validator
from validate_docbr import CPF
import re
from typing import Optional



def normalize_cpf(cpf: str) -> str:
    '''Remove todos os caracteres não numéricos de um CPF.'''
    if not cpf:
        return ""
    return re.sub(r'\D', '', cpf)



class EmployeeIn(BaseModel):
    '''Representa o schema de um funcionário para validação de dados na API.
    Usado ao criar um novo funcionário via endpoint.
    '''
    name: str
    job_title: str
    phone: str
    cpf: str

    @validator('cpf')
    def validate_and_normalize_cpf(cls, v):
        '''Valida o CPF e o retorna normalizado.'''
        normalized_cpf = normalize_cpf(v)

        cpf_validator = CPF()
        if not cpf_validator.validate(normalized_cpf):
            raise ValueError('CPF inválido')

        return normalized_cpf


class Employee(EmployeeIn):
    '''Schema para retornar um funcionário, incluindo o id.
    '''
    id: int

    class Config:
        from_attributes = True

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None

    class Config:
        from_attributes = True

    cpf: str