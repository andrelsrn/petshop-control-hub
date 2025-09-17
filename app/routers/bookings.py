from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import schemas, tables
from app.core.database import get_db
import re

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
    existing_booking = db.query(tables.Booking).filter(
        tables.Booking.employee_id == booking.employee_id,
        tables.Booking.scheduled_time == booking.scheduled_time).first()

    if existing_booking:
        raise HTTPException(
            status_code=409,
            detail=f"O funcionário já possui um agendamento neste horário ({booking.scheduled_time})."
    )

    db_booking = tables.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking