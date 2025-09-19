from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.core.database import get_db
import re

router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"]
)

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

    existing_customer = db.query(models.Customer).filter(
        models.Customer.phone == normalized_phone).first()

    if existing_customer:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um cliente cadastrado com este telefone. Cliente: {existing_customer.name}"
        )

    db_customer = models.Customer(
        name=customer.name,
        phone=normalized_phone,
        address=customer.address,
        cpf=customer.cpf
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=list[schemas.Customer])
def get_all_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de clientes com suporte a paginação.

    Este endpoint permite buscar clientes em lotes,
    especificando o número de registros a pular (`skip`) e o limite
    de resultados por página (`limit`). Se nenhum parâmetro for fornecido,
    retorna os primeiros 100 clientes.
    """
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=schemas.Customer)
def get_customer_by_id(customer_id: int, db: Session = Depends(get_db)):
    """
    Retorna um cliente pelo seu ID.
    
    Este endpoint  permite buscar o cliente pelo seu ID especificado.
    """

    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer

@router.get("/search/", response_model=list[schemas.CustomerSearchResult])
def search_customers_by_name(name: str, db: Session = Depends(get_db)):
    """
    Busca clientes com base no nome e retorna o nome e ID para identificação.
    
    Este endpoint otimizado retorna uma lista de objetos contendo
    apenas o ID e o nome dos clientes que correspondem à busca.
    """

    results = db.query(models.Customer.id, models.Customer.name).filter(
        models.Customer.name.ilike(f"%{name}%")).all()

    if not results:
        raise HTTPException(status_code=404, detail="Nenhum cliente encontrado")

    customers = [{"id": r[0], "name": r[1]} for r in results]

    return customers
        
@router.patch("/{customer_id}", response_model=schemas.Customer)
def update_customer(customer_id: int,
                    customer_update: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    '''Atualiza um cliente existente.
    
    Args:
        customer_id (int): O ID do cliente a ser atualizado.
        customer_update (schemas.CustomerUpdate): Os dados a serem atualizados.
        db (Session): A sessão do banco de dados para a operação.
        
    Raises:
        HTTPException: Exceção HTTP 404 se o cliente não for encontrado.
        
    Returns:
        models.Customer: O objeto do cliente atualizado.
    '''

    db_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id).first()
    
    if not db_customer:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )
    
    for key, value in customer_update.dict(exclude_unset=True).items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer