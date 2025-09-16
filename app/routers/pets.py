from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import schemas, tables
from app.core.database import get_db
import re

router = APIRouter()


@router.post("/", response_model=schemas.Pet)
def create_pet(pet: schemas.PetIn, db: Session = Depends(get_db)):
    '''Retorna um novo pet no  banco de dados.'''
    db_pet = tables.Pet(**pet.dict())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


@router.get("/", response_model=list[schemas.Pet])
def get_pets(db: Session = Depends(get_db)):
    '''Retorna a lista de pets no banco de dados.'''
    pets = db.query(tables.Pet).all()
    return pets