from fastapi import APIRouter, Depends, HTTPException,  Response, status
from sqlalchemy.orm import Session
from app import models
from app.core.database import get_db
from app.schemas import pet as schemas

router = APIRouter(
    prefix="/api/pets",
    tags=["Pets"]
)


def get_pet_or_404(pet_id: int, db: Session = Depends(get_db)):
    """
    Dependência que busca um funcionário ATIVO pelo ID.
    Lança HTTPException 404 se o funcionário não for encontrado ou estiver inativo.
    """
    db_pet = db.query(models.Pet).filter(
        models.Pet.id == pet_id).filter(
            models.Pet.is_active == True).first()

    if not db_pet:
        raise HTTPException(
            status_code=404,
            detail=f"Pet com ID {pet_id} não encontrado ou está inativo."
        )
    return db_pet


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
def get_all_pets(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
):
    
    """
    Retorna uma lista de pets com suporte a paginação.

    Este endpoint permite buscar pets em lotes, especificando o número
    de registros a pular (`skip`) e o limite de resultados por página (`limit`).
    Se nenhum parâmetro for fornecido, retorna os primeiros 100 pets.
    
    Permite a inclusao de pets inativos na lista.
    """
    
    query = db.query(models.Pet)
    
    if not include_inactive:
        query = query.filter(models.Pet.is_active == True)
    
    pets = query.offset(skip).limit(limit).all()
    return pets




@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(
        pet: models.Pet = Depends(get_pet_or_404),
        db: Session = Depends(get_db)):
    '''Soft delete de um pet pelo seu ID.

    Args:
        pet_id (int): O ID do pet a ser deletado.

        db (Session): A sessão do banco de dados, injetada pelo FastAPI.
    '''

    pet.is_active = False
    db.add(pet)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{pet_id}", response_model=schemas.Pet)
def update_pet(
        pet_update: schemas.PetUpdate,
        pet: models.Pet = Depends(get_pet_or_404),
        db: Session = Depends(get_db)):
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


    for key, value in pet_update.dict(exclude_unset=True).items():
        setattr(pet, key, value)

    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet