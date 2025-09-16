from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from . import models
from .core.database import SessionLocal, engine
from .models import schemas, tables
from sqlalchemy import func
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import re


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



@app.post("/api/sales", response_model=schemas.Sale)
def create_new_sale(sale: schemas.Sale, db: Session = Depends(get_db)):
    '''Cria uma nova venda no banco de dados e debita o estoque.

    Esta função verifica se o produto existe e se há quantidade 
    suficiente em estoque antes de registrar a venda.

    Args:
        sale (schemas.Sale): Objeto com os dados da venda a ser criada.
        db (Session): Sessão do banco de dados injetada pelo FastAPI.

    Raises:
        HTTPException 404: Se o produto não for encontrado no inventário.
        HTTPException 400: Se a quantidade em estoque for insuficiente.

    Returns:
        tables.Sale: O objeto da venda que foi salvo no banco de dados.
    '''
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



@app.post("/api/bookings", response_model=schemas.Booking)
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



def normalize_phone(phone: str) -> str:
    '''Remove todos os caracteres não numéricos de um número de telefone.'''
    if not phone:
        return ""
    return  re.sub(r'\D', '', phone)



@app.post("/api/customers", response_model=schemas.Customer)
def create_new_customer(customer: schemas.CustomerIn, db: Session = Depends(get_db)):
    """Cria um novo cliente após validar os dados e checar por duplicatas.

    Esta rota executa os seguintes passos:
    1. Normaliza o número de telefone removendo todos os caracteres não numéricos.
    2. Valida se o telefone fornecido não é vazio ou inválido.
    3. Verifica no banco de dados se já existe um cliente com o mesmo telefone normalizado.
    4. Se não houver duplicatas, cria e salva o novo cliente com o telefone já normalizado.

    Args:
        customer (schemas.CustomerIn): Os dados do novo cliente a ser criado.
        db (Session): A sessão do banco de dados, injetada pelo FastAPI.

    Raises:
        HTTPException 400 (Bad Request): Se o número de telefone for inválido.
        HTTPException 409 (Conflict): Se já existir um cliente com o mesmo telefone.

    Returns:
        schemas.Customer: O objeto do cliente que foi salvo no banco de dados.
    """
    normalized_phone = normalize_phone(customer.phone)

    if not normalized_phone:
        raise HTTPException(
            status_code=400,
              detail="Número de telefone inválido"
        )

    existing_customer = db.query(tables.Customer).filter(
        tables.Customer.phone == normalized_phone).first()
    
    if existing_customer:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um cliente cadastrado com este telefone. Cliente: {existing_customer.name}"
        )
    
    
    db_customer = tables.Customer(
        name=customer.name,
        phone=normalized_phone,
        address=customer.address
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.post("/api/employees", response_model=schemas.Employee)
def create_new_employee(employee: schemas.EmployeeIn, db: Session = Depends(get_db)):
    """Cria um novo funcionário após checar por duplicatas de CPF.

    A validação da estrutura e formato do CPF é realizada previamente no
    schema Pydantic (EmployeeIn). Esta função foca na regra de negócio de
    garantir que não exista mais de um funcionário com o mesmo CPF no sistema.

    Args:
        employee (schemas.EmployeeIn): Os dados validados do funcionário,
                                       já com o CPF normalizado.
        db (Session): A sessão do banco de dados injetada pelo FastAPI.

    Raises:
        HTTPException 409 (Conflict): Se já existir um funcionário cadastrado
                                      com o CPF fornecido.

    Returns:
        schemas.Employee: O objeto do funcionário que foi salvo no banco de dados.
    """
    existing_employee = db.query(tables.Employee).filter(
        tables.Employee.cpf == employee.cpf).first()
    
    if existing_employee:
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um funcionário cadastrado com este CPF. Funcionário: {existing_employee.name}"
        )

    db_employee = tables.Employee(
        name=employee.name,
        job_title=employee.job_title,
        phone=normalize_phone(employee.phone),
        cpf=employee.cpf
    )
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
