from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.core.database import get_db
from app.schemas import pet as schemas

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
    db_pet = models.Pet(**pet.dict())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


@router.get("/", response_model=list[schemas.Pet])
def get_all_pets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de pets com suporte a paginação.

    Este endpoint permite buscar pets em lotes, especificando o número
    de registros a pular (`skip`) e o limite de resultados por página (`limit`).
    Se nenhum parâmetro for fornecido, retorna os primeiros 100 pets.
    """
    pets = db.query(models.Pet).offset(skip).limit(limit).all()
    return pets


@router.delete("/{pet_id}", response_model=schemas.Pet)
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    '''Deleta um pet pelo seu ID.

    Args:
        pet_id (int): O ID do pet a ser deletado.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.
    '''
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not db_pet:
        raise HTTPException(
            status_code=404, detail="Pet não encontrado")
    db.delete(db_pet)
    db.commit()
    return db_pet


@router.patch("/{pet_id}", response_model=schemas.Pet)
def update_pet(pet_id: int,
               pet_update: schemas.PetUpdate, db: Session = Depends(get_db)):
    '''Atualiza um pet existente.

    Args:
        pet_id (int): O ID do pet a ser atualizado.
        pet_update (schemas.PetUpdate): Os dados a serem atualizados.
        db (Session): A sessão do banco de dados para a operação.

    Raises:
        HTTPException: Exceção HTTP 404 se o pet não for encontrado.

    Returns:
        models.Pet: O objeto do pet atualizado.
    '''
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()

    if not db_pet:
        raise HTTPException(
            status_code=404,
            detail="Pet não encontrado"
        )

    for key, value in pet_update.dict(exclude_unset=True).items():
        setattr(db_pet, key, value)

    db.commit()
    db.refresh(db_pet)
