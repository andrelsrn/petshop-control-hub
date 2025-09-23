from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.core.database import get_db
from app.schemas import inventory as schemas




router = APIRouter(
    prefix="/api/inventory",
    tags=["Inventory"]
)


def get_inventory_item_or_404(item_id: int, db: Session = Depends(get_db)):
    """
    Dependência que busca um item do inventário pelo ID.
    Lança HTTPException 404 se o item não for encontrado.
    Isso evita repetir a mesma lógica em várias rotas.
    """
    db_item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404,
                            detail=f"Item não encontrado com id {item_id}.")
    return db_item
    


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

    db_item = models.Inventory(**inventory_item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=list[schemas.Inventory])
def get_inventory_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    name: str | None = Query(None, description="Filtre por nome do produto(busca parcial)"),
    low_stock: bool | None=Query(None, description="Filtre por itens com estoque baixo")
):

    """
    Retorna uma lista de itens do inventário com filtros e paginação.
    - Use `?low_stock=true` para filtrar por estoque baixo.
    - Use `?name=Ração` para buscar itens por nome.
    - Use `?skip=0&limit=50` para paginar os resultados.
    """
    query = db.query(models.Inventory)

    if name:
        query = query.filter(models.Inventory.product_name.ilike(f"%{name}%"))

    if low_stock:
        query = query.filter(models.Inventory.quantity <= models.Inventory.low_stock_threshold)
    
    items = query.offset(skip).limit(limit).all()
    
    return items

    

@router.delete("/{item_id}", response_model=schemas.Inventory)
def delete_inventory_item(db_item: models.Inventory = Depends(get_inventory_item_or_404),
                          db: Session = Depends(get_db)):
    '''Deleta um item do inventário pelo seu ID.

    Args:
        item_id (int): O ID do item a ser deletado.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.
    '''

    db.delete(db_item)
    db.commit()
    return db_item  

@router.patch("/{item_id}", response_model=schemas.Inventory)
def update_inventory_item(item_update: schemas.InventoryUpdate,
                        db_item: models.Inventory = Depends(get_inventory_item_or_404),
                        db: Session = Depends(get_db)):
    '''Atualiza um item do inventário existente.

    Args:
        item_id (int): O ID do item a ser atualizado.
        item_update (schemas.InventoryUpdate): Os dados a serem atualizados.
        db (Session): A sessão do banco de dados para a operação.

    Raises:
        HTTPException: Exceção HTTP 404 se o item não for encontrado.

    Returns:
        models.Inventory: O objeto do item atualizado.
    '''  
    
    
    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{item_id}", response_model=schemas.Inventory)
def get_inventory_item_by_id(db_item: models.Inventory = Depends(get_inventory_item_or_404)):
    '''Retorna um item do inventário pelo seu ID.

    Args:
        item_id (int): O ID do item a ser buscado.
        db (Session): A sessão do banco de dados para a operação.

    Raises:
        HTTPException: Exceção HTTP 404 se o item não for encontrado.

    Returns:
        schemas.Inventory: O objeto do item solicitado.
    '''

    
    return db_item

