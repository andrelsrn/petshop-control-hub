from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import schemas, tables
from app.core.database import get_db
import re

router = APIRouter(
    prefix="/api/pets",
    tags=["Pets"]
)


@router.post("/", response_model=schemas.Pet)
def create_pet(pet: schemas.PetIn, db: Session = Depends(get_db)):
    """
    Cria um novo pet no banco de dados.

    Args:
        pet (schemas.PetIn): Dados do pet a ser criado.
        db (Session, optional): Sessão do banco de dados gerenciada pelo Depends(get_db).

    Returns:
        schemas.Pet: O pet criado, incluindo ID e demais campos persistidos no banco.
    """
    db_pet = tables.Pet(**pet.dict())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


@router.get("/", response_model=list[schemas.Pet])
def get_pets(db: Session = Depends(get_db)):
    """
    Retorna todos os pets cadastrados no banco de dados.

    Args:
        db (Session, optional): Sessão do banco de dados gerenciada pelo Depends(get_db).

    Returns:
        list[schemas.Pet]: Lista de todos os pets cadastrados.
    """
    pets = db.query(tables.Pet).all()
    return pets