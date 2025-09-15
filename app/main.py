from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from . import models
from .core.database import SessionLocal, engine
from .models import schemas, tables
from sqlalchemy import func
from datetime import date
from fastapi.middleware.cors import CORSMiddleware



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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Cria endpoint para registrar uma nova venda
@app.post("/api/events/new-sale", response_model=schemas.Sale)
def create_new_sale(sale: schemas.Sale, db: Session = Depends(get_db)):
    db_inventory_item = db.query(tables.Inventory).filter(
        tables.Inventory.product_name == sale.product_name).first()

    if not db_inventory_item:
        raise HTTPException(
            status_code=404, detail="Item não encontrado no inventário")

    if db_inventory_item.quantity < sale.quantity:
        raise HTTPException(status_code=400, detail="Fora de estoque")

    db_inventory_item.quantity -= sale.quantity
    db_sale = tables.Sale(
        product_name=sale.product_name,
        quantity=sale.quantity,
        total_value=sale.total_value,
        customer_id=sale.customer_id)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


# Cria endpoint para agendar um serviço
@app.post("/api/events/new-booking", response_model=schemas.Booking)
def create_new_booking(booking: schemas.Booking, db: Session = Depends(get_db)):
    db_booking = tables.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


# Cria endpoint para registrar um novo cliente
@app.post("/api/events/new-customer", response_model=schemas.Customer)
def create_new_customer(customer: schemas.CustomerIn, db: Session = Depends(get_db)):
    db_customer = tables.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.post("/api/events/new-employee", response_model=schemas.Employee)
def create_new_employee(employee: schemas.EmployeeIn, db: Session = Depends(get_db)):
    db_employee = tables.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.get("/api/sales/", response_model=list[schemas.Sale])
def get_all_sales(db: Session = Depends(get_db)):
    '''Retorna a lista de todas as vendas registradas  no banco de dados.
    '''
    sales = db.query(tables.Sale).all()
    return sales


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


@app.post("/api/pets/", response_model=schemas.Pet)
def create_pet(pet: schemas.PetIn, db: Session = Depends(get_db)):
    '''Retorna um novo pet no  banco de dados.'''
    db_pet = tables.Pet(**pet.dict())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


@app.get("/api/pets/", response_model=list[schemas.Pet])
def get_pets(db: Session = Depends(get_db)):
    '''Retorna a lista de pets no banco de dados.'''
    pets = db.query(tables.Pet).all()
    return pets
