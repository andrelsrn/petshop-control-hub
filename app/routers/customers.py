from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app import models
from app.core.database import get_db
from app.schemas import customer as schemas


router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"]
)



def get_customer_or_404(customer_id: int, db: Session = Depends(get_db)):
    """
    Dependência que busca um cliente ATIVO pelo ID.
    Lança HTTPException 404 se o cliente não for encontrado ou estiver inativo.
    """
    db_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.is_active == True
    ).first()

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com id {customer_id} não encontrado"
        )
    return db_customer


@router.post("/", response_model=schemas.Customer, status_code=status.HTTP_201_CREATED)
def create_new_customer(customer: schemas.CustomerIn, db: Session = Depends(get_db)):
    """Cria um novo cliente.

    A validação e normalização do CPF e telefone são feitas automaticamente pelo schema CustomerIn.
    Esta rota apenas verifica a duplicidade de CPF no banco de dados.
    """

    existing_customer = db.query(models.Customer).filter(
        models.Customer.cpf == customer.cpf).first()

    if existing_customer:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um cliente cadastrado com este CPF. Cliente: {existing_customer.name}"
        )

    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/", response_model=list[schemas.Customer])
def get_all_customers(skip: int = 0, limit: int = 100,
                      db: Session = Depends(get_db)):
    """
    Retorna uma lista de clientes com suporte a paginação.

    Este endpoint permite buscar clientes em lotes,
    especificando o número de registros a pular (`skip`) e o limite
    de resultados por página (`limit`). Se nenhum parâmetro for fornecido,
    retorna os primeiros 100 clientes.
    """
    customers = db.query(models.Customer).filter(
        models.Customer.is_active == True
    ).offset(skip).limit(limit).all()

    return customers


@router.get("/{customer_id}", response_model=schemas.Customer)
def get_customer_by_id(
        customer: models.Customer = Depends(get_customer_or_404)):
    """
    Retorna um cliente pelo seu ID.

    Este endpoint  permite buscar o cliente pelo seu ID especificado.
    """
    return customer



@router.get("/search/", response_model=list[schemas.CustomerSearchResult])
def search_customers_by_name(name: str, db: Session = Depends(get_db)):
    """
    Busca clientes com base no nome e retorna o nome e ID para identificação.

    Este endpoint otimizado retorna uma lista de objetos contendo
    apenas o ID e o nome dos clientes que correspondem à busca.
    """

    results = db.query(models.Customer.id, models.Customer.name).filter(
        models.Customer.is_active == True,
        models.Customer.name.ilike(f"%{name}%")).all()

    if not results:
        raise HTTPException(
            status_code=404, detail="Nenhum cliente encontrado")

    customers = [{"id": r[0], "name": r[1]} for r in results]

    return customers


@router.patch("/{customer_id}", response_model=schemas.Customer)
def update_customer(
        customer_update: schemas.CustomerUpdate,
        db_customer: models.Customer = Depends(get_customer_or_404),
        db: Session = Depends(get_db)):
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

    for key, value in customer_update.dict(exclude_unset=True).items():
        setattr(db_customer, key, value)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer: models.Customer = Depends(get_customer_or_404),
    db: Session = Depends(get_db)
):
    '''Deleta um cliente pelo seu ID.

    Args:
        customer_id (int): O ID do cliente a ser deletado.
    '''
    customer.is_active = False
    db.add(customer)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
