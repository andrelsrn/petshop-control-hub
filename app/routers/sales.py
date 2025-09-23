from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
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


def get_sale_or_404(sale_id: int, db: Session = Depends(get_db)):
    '''Dependência que busca uma venda pelo ID.

    Lança HTTPException 404 se a venda não for encontrada.
    '''
    db_sale = db.query(models.Sale).filter(
        models.Sale.id == sale_id).filter(
            models.Sale.is_active == True).first()

    if not db_sale:
        raise HTTPException(
            status_code=404,
            detail="Venda não encontrada"
        )

    return db_sale


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

    try:
        db_inventory_item.quantity -= sale.quantity
        db.add(db_inventory_item)

        db_sale = models.Sale(**sale.dict())
        db.add(db_sale)
        db.commit()
        db.refresh(db_sale)
        db.refresh(db_inventory_item)
        return db_sale
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Nao foi possivel criar a venda")




@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale: models.Sale = Depends(get_sale_or_404),
    db: Session = Depends(get_db)
):
    '''Soft delete de uma venda pelo seu ID.

    Args:
        sale_id (int): O ID da venda a ser deletada.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        Response: Uma resposta HTTP com o status 204 (No Content) em caso de sucesso.
    '''
    sale.is_active = False
    db.add(sale)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{sale_id}", response_model=schemas.Sale)
def get_sale_by_id(
        sale: models.Sale = Depends(get_sale_or_404),
        db: Session = Depends(get_db)):
    '''Retorna uma venda pelo seu ID.

    Args:
        sale_id (int): O ID da venda a ser buscada.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Raises:
        HTTPException: Exceção HTTP 404 se a venda não for encontrada.

    Returns:
        schemas.Sale: O objeto da venda solicitado.
    '''

    return sale


@router.get("/", response_model=list[schemas.Sale])
def get_sales(
    db: Session = Depends(get_db),
    month: Optional[int] = Query(
        None, ge=1, le=12, description="Filtra vendas por mês"),
    year: Optional[int] = Query(None, description="Filtra vendas por ano")
):
    """
    Retorna uma lista de vendas.

    - Se nenhum parâmetro for fornecido, retorna todas as vendas.
    - Se os parâmetros 'month' e 'year' forem fornecidos, 
      retorna as vendas filtradas por esse período.
    """
    query = db.query(models.Sale).filter(models.Sale.is_active == True)

    # Aplica o filtro apenas se ambos os parâmetros forem fornecidos
    if month is not None and year is not None:
        query = query.filter(
            extract('month', models.Sale.created_at) == month,
            extract('year', models.Sale.created_at) == year
        )

    sales = query.all()
    return sales
