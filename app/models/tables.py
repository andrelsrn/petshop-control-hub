from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from ..database import Base


class Sale(Base):
    '''Representa a tabela de vendas no banco de dados.'''
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, comment="Identificador único da venda.")
    product_id = Column(String, index=True, comment="Identificador único do produto.")
    quantity = Column(Integer, comment="Quantidade do produto comprado.")
    total_value = Column(Float, comment="Valor total da venda.")
    customer_id = Column(String, index=True, comment="Identificador único do cliente.")

class Booking(Base):
    '''Representa a tabela de agendamentos no banco de dados.'''
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, comment="Identificador único do agendamento.")
    service_name = Column(String, index=True, comment="Nome do serviço agendado.")
    pet_id = Column(String, index=True, comment="Identificador único do pet agendado.")
    scheduled_time = Column(DateTime, index=True, comment="Horário agendado para o serviço.")
    employee_id = Column(String, index=True, comment="Identificador único do funcionário responsável pelo serviço.")
    delivery = Column(Boolean, comment="Indica se o cliente solicitou o serviço de busca e entrega")

class Customer(Base):
    '''Representa a tabela de clientes no banco de dados.'''
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, comment="Identificador único do cliente.")
    name = Column(String, index=True, comment="Nome do cliente.")
    phone = Column(String, index=True, comment="Número de telefone do cliente.")
    address = Column(String, index=True, comment="Endereço do cliente.")
    pet_name = Column(String, index=True, comment="Nome do pet do cliente.")
    pet_breed = Column(String, index=True, comment="Raça do pet do cliente.")  