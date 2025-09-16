from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from ..core.database import Base
from sqlalchemy.orm import relationship



class Sale(Base):
    '''Representa a tabela de vendas no banco de dados.'''
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True,
                comment="Identificador único da venda.")
    
    product_name = Column(String, index=True,
                          comment="Identificador único do produto.")
    quantity = Column(Integer, comment="Quantidade do produto comprado.")
    total_value = Column(Float, comment="Valor total da venda.")
    customer_id = Column(Integer, index=True,
                         comment="Identificador único do cliente.")


class Booking(Base):
    '''Representa a tabela de agendamentos no banco de dados.'''
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True,
                comment="Identificador único do agendamento.")
    service_name = Column(String, index=True,
                          comment="Nome do serviço agendado.")
    pet_id = Column(String, ForeignKey("pets.id"), index=True,
                    comment="Identificador único do pet.")
    scheduled_time = Column(DateTime, index=True,
                            comment="Horário agendado para o serviço.")
    employee_id = Column(
        Integer, ForeignKey("employees.id"), index=True, comment="Identificador único do funcionário.")
    delivery = Column(
        Boolean, comment="Indica se o cliente solicitou o serviço de busca e entrega")
    pet = relationship("Pet", back_populates="bookings")
    employee = relationship("Employee", back_populates="bookings")


class Customer(Base):
    '''Representa a tabela de clientes no banco de dados.'''
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True,
                comment="Identificador único do cliente.")
    
    name = Column(String(100), index=True, nullable=False,
                  comment="Nome do cliente.")
    
    phone = Column(String(20), unique=True, index=True, nullable=False,
                   comment="Número de telefone único e normalizado do cliente.")
    
    address = Column(String(255), nullable=True,
                     comment="Endereço do cliente (opcional).")


class Employee(Base):
    '''Representa a tabela de funcionários no banco de dados.c'''
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True,
                comment="Identificador único do funcionário.")
    
    name = Column(String(100), index=True, nullable=False,
                  comment="Nome do funcionário.")

    job_title = Column(String(100), index=True, comment="Cargo do funcionário.")

    phone = Column(String(20), index=True,
                   comment="Número de telefone do funcionário.")
    
    cpf = Column(String(11), unique=True, index=True, nullable=False,
                 comment="CPF único e normalizado do funcionário.")
    
    bookings = relationship("Booking", back_populates="employee")


class Inventory(Base):
    '''Representa a tabela de inventário dos produtos no banco de dados.'''
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True,
                comment="Identificador único do produto no inventário.")
    product_name = Column(String, index=True, comment="Nome do produto.")
    quantity = Column(Integer, comment="Quantidade disponível do produto.")
    price = Column(Float, comment="Preço do produto.")
    low_stock_threshold = Column(Integer, comment="Limite de estoque baixo.")


class Pet(Base):
    '''Representa a tabela de pets no banco de dados.'''
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True,
                comment="Identificador único do pet.")
    name = Column(String, index=True, comment="Nome do pet.")
    breed = Column(String, index=True, comment="Raça do pet.")
    date_of_birth = Column(DateTime, index=True,
                           comment="Data de nascimento do pet.")
    customer_id = Column(Integer, ForeignKey("customers.id"),
                         index=True, comment="Identificador único do cliente.")
    bookings = relationship("Booking", back_populates="pet")


class Vaccine(Base):
    '''Representa a tabela de vacinas no banco de dados.'''
    __tablename__ = "vaccines"

    id = Column(Integer, primary_key=True, index=True,
                comment="Identificador único da vacina.")
    pet_id = Column(Integer, ForeignKey("pets.id"), index=True,
                    comment="Identificador único do pet.")
    vaccine_name = Column(String, index=True, comment="Nome da vacina.")
    date_of_application = Column(
        DateTime, index=True, comment="Data da aplicação da vacina.")
