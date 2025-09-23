from pydantic import BaseModel
from datetime import datetime




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

class InventoryUpdate(BaseModel):
    product_name: str | None = None
    quantity: int | None = None
    price: float | None = None
    low_stock_threshold: int | None = None

    class Config:
        from_attributes = True