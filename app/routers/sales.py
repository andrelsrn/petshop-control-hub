from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models
from app.core.database import get_db
from app.schemas import sale as schemas
from sqlalchemy import extract
from typing import Optional




router = APIRouter(
    prefix="/api/sales",
    tags=["Sales"]
)


@router.post("/", response_model=schemas.Sale)
def create_new_sale(sale: schemas.Sale, db: Session = Depends(get_db)):
    '''Cria uma nova venda no banco de dados e debita o estoque.

    Esta função verifica se o produto existe e se há quantidade
    suficiente em estoque antes de registrar a venda.

    Args:
        sale (schemas.Sale): Objeto com os dados da venda a ser criada.
        db (Session): Sessão do banco de dados injetada pelo FastAPI.

    Raises:
        HTTPException 404: Se o produto não for encontrado no inventário.
        HTTPException 400: Se a quantidade em estoque for insuficiente.

    Returns:
        tables.Sale: O objeto da venda que foi salvo no banco de dados.
    '''
    db_inventory_item = db.query(models.Inventory).filter(
        models.Inventory.product_name == sale.product_name).first()

    if not db_inventory_item:
        raise HTTPException(
            status_code=404, detail="Item não encontrado no inventário")

    if db_inventory_item.quantity < sale.quantity:
        raise HTTPException(status_code=400, detail="Fora de estoque")

    db_inventory_item.quantity -= sale.quantity
    db_sale = models.Sale(
        product_name=sale.product_name,
        quantity=sale.quantity,
        total_value=sale.total_value,
        customer_id=sale.customer_id)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale




@router.delete("/{sale_id}", response_model=schemas.Sale)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    '''Deleta uma venda pelo seu ID.

    Args:
        sale_id (int): O ID da venda a ser deletada.
        db (Session): A sessão do banco de dados para a operação.

    Raises:
        HTTPException: Exceção HTTP 404 se a venda não for encontrada.

    Returns:
        schemas.Sale: O objeto da venda que foi deletada.
    '''

    db_sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()

    if not db_sale:
        raise HTTPException(
            status_code=404,
            detail="Venda não encontrada"
        )

    db.delete(db_sale)
    db.commit()
    return db_sale


@router.get("/{sale_id}", response_model=schemas.Sale)
def get_sale_by_id(sale_id: int, db: Session = Depends(get_db)):
    '''Retorna uma venda pelo seu ID.

    Args:
        sale_id (int): O ID da venda a ser buscada.
        db (Session): A sessão do banco de dados para a operação.
        '''

    db_sale_id = db.query(models.Sale).filter(
        models.Sale.id == sale_id).first()

    if not db_sale_id:
        raise HTTPException(
            status_code=404,
            detail="Venda não encontrada"
        )

    return db_sale_id


@router.get("/", response_model=list[schemas.Sale])
def get_sales(
    db: Session = Depends(get_db),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filtra vendas por mês"),
    year: Optional[int] = Query(None, description="Filtra vendas por ano")
):
    """
    Retorna uma lista de vendas.
    
    - Se nenhum parâmetro for fornecido, retorna todas as vendas.
    - Se os parâmetros 'month' e 'year' forem fornecidos, 
      retorna as vendas filtradas por esse período.
    """
    query = db.query(models.Sale)

    # Aplica o filtro apenas se ambos os parâmetros forem fornecidos
    if month is not None and year is not None:
        query = query.filter(
            extract('month', models.Sale.date) == month,
            extract('year', models.Sale.date) == year
        )
    
    sales = query.all()
    return sales
