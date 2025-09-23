from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.core.database import get_db
import re
from app.schemas import employee as schemas


router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)


def normalize_phone(phone: str) -> str:
    '''Remove todos os caracteres não numéricos de um número de telefone.'''
    if not phone:
        return ""
    return re.sub(r'\D', '', phone)


@router.post("/", response_model=schemas.Employee)
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

    db_employee = models.Employee(
        name=employee.name,
        job_title=employee.job_title,
        phone=normalize_phone(employee.phone),
        cpf=employee.cpf
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.delete("/{employee_id}", response_model=schemas.Employee)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Deleta um funcionário pelo seu ID.

    Args:
        employee_id (int): O ID do funcionário a ser deletado.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI."""

    db_employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(
            status_code=404, detail="Funcionário não encontrado")
    
    db.delete(db_employee)
    db.commit()
    return db_employee

@router.patch("/{employee_id}", response_model=schemas.Employee)
def update_employee(employee_id: int,
                    employee_update: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
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

    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Funcionário não encontrado, tente novamente"
        )
    
    for key, value in employee_update.dict(exclude_unset=True).items():
        setattr(employee, key, value)
    
    db.commit()
    db.refresh(employee)
    return employee

@router.get("/", response_model=list[schemas.Employee])
def get_all_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    '''Retorna uma lista de funcionários com suporte a paginação.
    
    Este endpoint permite buscar funcionários em lotes, especificando o número
    de registros a pular (`skip`) e o limite de resultados por página (`limit`).
    Se nenhum parâmetro for fornecido, retorna os primeiros 100 funcionários.
    '''
    employees = db.query(models.Employee).offset(skip).limit(limit).all()
    return employees