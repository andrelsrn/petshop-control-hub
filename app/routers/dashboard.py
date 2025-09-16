from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import schemas, tables
from app.core.database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard & KPIs"]
)


@router.get("/", response_model=schemas.KPIs)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Retorna um resumo com os principais indicadores de desempenho (KPIs) do negócio.

    Este endpoint serve como a principal fonte de dados para um painel de
    controle geral, agregando métricas de vendas, agendamentos e clientes.

    A URL final deste endpoint é a combinação do prefixo do router com a
    rota definida aqui (ex: GET /api/dashboard/).

    Args:
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Returns:
        schemas.KPIs: Um objeto contendo a receita total, o número total
                      de vendas, agendamentos e clientes.
    """

    total_revenue_result = db.query(func.sum(tables.Sale.total_value)).scalar()
    total_revenue = total_revenue_result or 0.0

    total_sales = db.query(func.count(tables.Sale.id)).scalar()
    total_bookings = db.query(func.count(tables.Booking.id)).scalar()
    total_customers = db.query(func.count(tables.Customer.id)).scalar()

    return schemas.KPIs(
        total_revenue=total_revenue,
        total_sales=total_sales,
        total_bookings=total_bookings,
        total_customers=total_customers
    )
