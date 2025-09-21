from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app import models
from app.schemas import booking as schemas
from app.core.database import get_db

router = APIRouter(
    prefix="/api/bookings",
    tags=["Bookings"]
)


@router.post("/", response_model=schemas.Booking)
def create_new_booking(booking: schemas.Booking, db: Session = Depends(get_db)):
    """Cria um novo agendamento após verificar a disponibilidade de horário.

    Esta rota primeiro consulta o banco de dados para garantir que não existe
    outro agendamento para o mesmo funcionário no mesmo horário. Se o horário
    estiver livre, o novo agendamento é criado.

    Args:
        booking (schemas.Booking): Os dados do novo agendamento a ser criado.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Raises:
        HTTPException: Com status 409 (Conflict), caso o horário já esteja
                       ocupado para o funcionário especificado.

    Returns:
        tables.Booking: O objeto do agendamento que foi salvo no banco de dados.
    """
    existing_booking = db.query(models.Booking).filter(
        models.Booking.employee_id == booking.employee_id,
        models.Booking.scheduled_time == booking.scheduled_time).first()

    if existing_booking:
        raise HTTPException(
            status_code=409,
            detail=f"O funcionário já possui um agendamento neste horário ({booking.scheduled_time})."
        )

    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    """Deleta um agendamento pelo seu ID.

    Args:
        booking_id (int): O ID do agendamento a ser deletado.

    Returns:
        Response: Uma resposta HTTP com o status 204 (No Content) em caso de sucesso.
    """

    db_booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id).first()

    if not db_booking:
        raise HTTPException(
            status_code=404, detail="Agendamento não encontrado")

    db.delete(db_booking)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{booking_id}", response_model=schemas.Booking)
def update_booking(booking_id: int,
                    booking_update: schemas.BookingUpdate, db: Session = Depends(get_db)):
    """Atualiza um agendamento existente.

    Args:
        booking_id (int): O ID do agendamento a ser atualizado.
        booking_update (schemas.BookingUpdate): Os dados a serem atualizados.
        db (Session): A sessão do banco de dados para a operação.
        
    Raises:
        HTTPException: Exceção HTTP 404 se o agendamento não for encontrado.
        
    Returns:
        models.Booking: O objeto do agendamento atualizado.
    """
    
    db_booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id).first()
    
    if not db_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
             detail="Agendamento não encontrado"
        )
    
    for key, value in booking_update.dict(exclude_unset=True).items():
        setattr(db_booking, key, value)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking


@router.get("/", response_model=list[schemas.Booking])
def get_all_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retorna uma lista de agendamentos com suporte a paginação.
    
    Este endpoint permite buscar agendamentos em lotes, especificando o número
    de registros a pular (`skip`) e o limite de resultados por página (`limit`).
    Se nenhum parâmetro for fornecido, retorna os primeiros 100 agendamentos.
    """
    bookings = db.query(models.Booking).offset(skip).limit(limit).all()
    return bookings

@router.get("/{booking_id}", response_model=schemas.Booking)
def get_booking_by_id(booking_id:int, db: Session = Depends(get_db)):
    """Busca um agendamento específico pelo ID.

    Args:
        booking_id (int): O ID do agendamento a ser buscado.
        db (Session): A sessão do banco de dados para a operação.

    Raises:
        HTTPException: Exceção HTTP 404 se o agendamento não for encontrado.

    Returns:
        schemas.Booking: O objeto do agendamento solicitado.
    """
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
    )

    return booking

