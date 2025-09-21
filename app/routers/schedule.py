from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from datetime import date
from app import models
from app.core.database import get_db
from sqlalchemy import func
from app.schemas import booking as schemas




router = APIRouter(
    prefix="/api/schedule",
    tags=["Schedule"]
)


@router.get("/", response_model=list[schemas.BookingResponse])
def get_todays_schedule(db: Session = Depends(get_db)):
    """
    Retorna uma lista com todos os agendamentos agendados para o dia de hoje.

    Este endpoint realiza uma consulta para buscar todos os registros da tabela de agendamentos
    que possuem a data programada igual ao dia atual. Inclui os dados do pet e do funcionário
    relacionados a cada agendamento.

    A URL final será a combinação do prefixo do router de agendamentos com a rota definida aqui
    (ex: GET /api/schedule/).

    Args:
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        list[schemas.BookingResponse]: Uma lista de objetos, onde cada objeto representa
        um agendamento do dia, com informações do pet e do funcionário.
    """
    today = date.today()
    bookings_today = db.query(models.Booking).options(
        selectinload(models.Booking.pet),
        selectinload(models.Booking.employee)
    ).filter(
        func.date(models.Booking.scheduled_time) == today
    ).all()

    return bookings_today
