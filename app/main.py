from fastapi import FastAPI
from .core.database import SessionLocal, engine
from .models import schemas, tables
from fastapi.middleware.cors import CORSMiddleware
from .routers import customers, bookings, sales, employees, pets, dashboard, inventory, schedule


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


app.include_router(customers.router)

app.include_router(bookings.router)

app.include_router(schedule.router)

app.include_router(sales.router)

app.include_router(employees.router)

app.include_router(pets.router)

app.include_router(dashboard.router)

app.include_router(inventory.router)
