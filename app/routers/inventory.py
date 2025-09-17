from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models import schemas, tables
from app.core.database import get_db


router = APIRouter(
    prefix="/api/inventory",
    tags=["Inventory"]
)


@router.post("/", response_model=schemas.Inventory)
def create_inventory_item(inventory_item: schemas.InventoryIn, db: Session = Depends(get_db)):
    """
    Cria um novo item no inventário.

    Args:
        inventory_item (schemas.InventoryIn): Dados do item a ser criado no inventário.
        db (Session, optional): Sessão do banco de dados, gerenciada pelo Depends(get_db).

    Returns:
        schemas.Inventory: O item do inventário criado, incluindo seu ID e demais campos persistidos.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: Caso ocorra algum erro durante a inserção no banco.

    HTTP Method:
        POST

    Endpoint:
        /api/inventory/
    """
    db_item = tables.Inventory(**inventory_item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=list[schemas.Inventory])
def get_inventory_items(
    low_stock: bool | None=Query(None, description="Filtre por itens com estoque baixo"),
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista de itens do inventário.
    - Use o parâmetro `?low_stock=true` para filtrar apenas itens com estoque baixo.
    """
    query = db.query(tables.Inventory)
    if low_stock:
        query = query.filter(tables.Inventory.quantity <= tables.Inventory.low_stock_threshold)

    return query.all()