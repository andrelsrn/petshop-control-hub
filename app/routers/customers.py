from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import schemas, tables
from app.core.database import get_db
import re

router = APIRouter()

def normalize_phone(phone: str) -> str:
    '''Remove todos os caracteres não numéricos de um número de telefone.'''
    if not phone:
        return ""
    return re.sub(r'\D', '', phone)


@router.post("/", response_model=schemas.Customer)
def create_new_customer(customer: schemas.CustomerIn, db: Session = Depends(get_db)):
    """Cria um novo cliente após validar os dados e checar por duplicatas.

    Esta rota executa os seguintes passos:
    1. Normaliza o número de telefone removendo todos os caracteres não numéricos.
    2. Valida se o telefone fornecido não é vazio ou inválido.
    3. Verifica no banco de dados se já existe um cliente com o mesmo telefone normalizado.
    4. Se não houver duplicatas, cria e salva o novo cliente com o telefone já normalizado.

    Args:
        customer (schemas.CustomerIn): Os dados do novo cliente a ser criado.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Raises:
        HTTPException 400 (Bad Request): Se o número de telefone for inválido.
        HTTPException 409 (Conflict): Se já existir um cliente com o mesmo telefone.

    Returns:
        schemas.Customer: O objeto do cliente que foi salvo no banco de dados.
    """
    normalized_phone = normalize_phone(customer.phone)

    if not normalized_phone:
        raise HTTPException(
            status_code=400,
            detail="Número de telefone inválido"
        )

    existing_customer = db.query(tables.Customer).filter(
        tables.Customer.phone == normalized_phone).first()

    if existing_customer:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um cliente cadastrado com este telefone. Cliente: {existing_customer.name}"
        )

    db_customer = tables.Customer(
        name=customer.name,
        phone=normalized_phone,
        address=customer.address
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer
