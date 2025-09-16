from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import schemas, tables
from app.core.database import get_db
import re

router = APIRouter()



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
    db_inventory_item = db.query(tables.Inventory).filter(
        tables.Inventory.product_name == sale.product_name).first()

    if not db_inventory_item:
        raise HTTPException(
            status_code=404, detail="Item não encontrado no inventário")

    if db_inventory_item.quantity < sale.quantity:
        raise HTTPException(status_code=400, detail="Fora de estoque")

    db_inventory_item.quantity -= sale.quantity
    db_sale = tables.Sale(
        product_name=sale.product_name,
        quantity=sale.quantity,
        total_value=sale.total_value,
        customer_id=sale.customer_id)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale



@router.get("/", response_model=list[schemas.Sale])
def get_all_sales(db: Session = Depends(get_db)):
    """Retorna uma lista com todas as vendas registradas no sistema.

    Este endpoint realiza uma consulta para buscar todos os registros da
    tabela de vendas sem aplicar nenhum filtro.

    A URL final será a combinação do prefixo do router de vendas com a
    rota definida aqui (ex: GET /api/sales/).

    Args:
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        list[schemas.Sale]: Uma lista de objetos, onde cada objeto
                            representa uma venda registrada.
    """
    sales = db.query(tables.Sale).all()
    return sales
