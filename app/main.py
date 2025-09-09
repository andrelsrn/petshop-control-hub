from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal, engine
from .models import schemas, tables


tables.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Pet Control Hub", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Cria endpoint para registrar uma nova venda
@app.post("/api/events/new-sale", response_model=schemas.Sale)
def create_new_sale(sale: schemas.Sale, db: Session = Depends(get_db)):
    db_sale = tables.Sale(**sale.dict())
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
def create_new_customer(customer: schemas.Customer, db: Session = Depends(get_db)):
    db_customer = tables.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

