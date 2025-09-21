from pydantic import BaseModel


class Sale(BaseModel):
    '''
    Representa o schema de uma venda para validação de dados na API.
    Usado ao criar uma nova venda via endpoint.
    '''
    product_name: str
    quantity: int
    total_value: float
    customer_id: int