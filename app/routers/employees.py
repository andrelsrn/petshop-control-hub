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
    return  re.sub(r'\D', '', phone)

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