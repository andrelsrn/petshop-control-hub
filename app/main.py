from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from . import models
from .core.database import SessionLocal, engine
from .models import schemas, tables
from sqlalchemy import func
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import re
from .routers import customers, bookings, sales, employees, pets, dashboard
from .core.database import get_db




tables.Base.metadata.create_all(bind=engine)



app = FastAPI(title="Pet Control Hub", version="1.0.0")


# Lista de origens que podem acessar a API
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Adiciona o middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])

app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])

app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])

app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])

app.include_router(pets.router, prefix="/api/pets", tags=["Pets"])

app.include_router(dashboard.router)





@app.get("/api/dashboard/kpis/", response_model=schemas.KPIs)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    '''Calcula e retorna os principais  indicadores do negocio.'''

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


@app.get("/api/schedule/today/", response_model=list[schemas.BookingResponse])
def get_todays_schedule(db: Session = Depends(get_db)):
    """
    Retorna a lista de todos os agendamentos agendados para o dia de hoje.
    """
    today = date.today()
    bookings_today = db.query(tables.Booking).options(
    selectinload(tables.Booking.pet),
    selectinload(tables.Booking.employee)
    ).filter(
        func.date(tables.Booking.scheduled_time) == today
    ).all()

    return bookings_today


@app.post("/api/inventory/", response_model=schemas.Inventory)
def create_inventory_item(inventory_item: schemas.InventoryIn, db: Session = Depends(get_db)):
    '''Cria um novo item no inventário.'''
    db_item = tables.Inventory(**inventory_item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/api/alert/low-stock/", response_model=list[schemas.Inventory])
def get_low_stock_items(db: Session = Depends(get_db)):
    '''Retorna a lista de itens com estoque baixo.'''
    low_stock_items = db.query(tables.Inventory).filter(
        tables.Inventory.quantity <= tables.Inventory.low_stock_threshold).all()
    return low_stock_items



