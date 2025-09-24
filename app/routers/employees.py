from fastapi import APIRouter, Depends, HTTPException, status,  Response
from sqlalchemy.orm import Session
from app import models
from app.core.database import get_db
import re
from app.schemas import employee as schemas


router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)


def get_employee_or_404(employee_id: int, db: Session = Depends(get_db)):
    """
    Dependência que busca um funcionário ATIVO pelo ID.
    Lança HTTPException 404 se o funcionário não for encontrado ou estiver inativo.
    """
    db_employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id,
        models.Employee.is_active == True
    ).first()
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionário com id {employee_id} não encontrado ou está inativo."
        )
    return db_employee


def normalize_phone(phone: str) -> str:
    '''Remove todos os caracteres não numéricos de um número de telefone.'''
    if not phone:
        return ""
    return re.sub(r'\D', '', phone)


@router.post("/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED)
def create_new_employee(employee: schemas.EmployeeIn, db: Session = Depends(get_db)):
    """Cria um novo funcionário após checar por duplicatas de CPF.

    A validação da estrutura e formato do CPF é realizada previamente no
    schema Pydantic (EmployeeIn). Esta função foca na regra de negócio de
    garantir que não exista mais de um funcionário com o mesmo CPF no sistema.

    Args:
        employee (schemas.EmployeeIn): Os dados validados do funcionário,
                                       já com o CPF normalizado.
        db (Session): A sessão do banco de dados injetada pelo FastAPI.

    Raises:
        HTTPException 409 (Conflict): Se já existir um funcionário cadastrado
                                      com o CPF fornecido.

    Returns:
        schemas.Employee: O objeto do funcionário que foi salvo no banco de dados.
    """

    existing_employee = db.query(models.Employee).filter(
        models.Employee.cpf == employee.cpf).first()

    if existing_employee:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um funcionário cadastrado com este CPF. Funcionário: {existing_employee.name}"
        )

    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
        employee: models.Employee = Depends(get_employee_or_404),
        db: Session = Depends(get_db)):
    '''Soft delete de um funcionario pelo seu ID.

    Args:
        employee_id (int): O ID do funcionario a ser deletado.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        Response: Uma resposta HTTP com o status 204 (No Content) em caso de sucesso.
    '''

    employee.is_active = False
    db.add(employee)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{employee_id}", response_model=schemas.Employee)
def update_employee(
        employee_update: schemas.EmployeeUpdate,
        db_employee: models.Employee = Depends(get_employee_or_404),
        db: Session = Depends(get_db)):
    '''Atualiza um funcionário existente.

    Args:
        employee_id (int): O ID do funcionário a ser atualizado.
        employee_update (schemas.EmployeeUpdate): Os dados a serem atualizados.
        db (Session): A sessão do banco de dados para a operação.

    Raises:
        HTTPException: Exceção HTTP 404 se o funcionário não for encontrado.

    Returns:
        models.Employee: O objeto do funcionário atualizado.
    '''

    for key, value in employee_update.dict(exclude_unset=True).items():
        setattr(db_employee, key, value)

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.get("/", response_model=list[schemas.Employee])
def get_all_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    '''Retorna uma lista de funcionários com suporte a paginação.

    Este endpoint permite buscar funcionários em lotes, especificando o número
    de registros a pular (`skip`) e o limite de resultados por página (`limit`).
    Se nenhum parâmetro for fornecido, retorna os primeiros 100 funcionários.
    '''
    employees = db.query(models.Employee).filter(
        models.Employee.is_active == True).offset(skip).limit(limit).all()

    return employees


@router.get("/{employee_id}", response_model=schemas.Employee)
def get_employee_by_id(
    employee: models.Employee = Depends(get_employee_or_404)
):
    """Retorna um funcionário ativo pelo seu ID."""
    return employee
