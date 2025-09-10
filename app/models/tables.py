from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from ..core.database import Base


class Sale(Base):
    '''Representa a tabela de vendas no banco de dados.'''
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, comment="Identificador único da venda.")
    product_name = Column(String, index=True, comment="Identificador único do produto.") #troquei o nome para ser  igual, ao nome no inventario
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
  

class Inventory(Base):
    '''Representa a tabela de inventário dos produtos no banco de dados.'''
    __tablename__ = "inventory"

    id = Column(Integer,primary_key=True, index=True, comment="Identificador único do produto no inventário.")
    product_name = Column(String, index=True, comment="Nome do produto.")
    quantity = Column(Integer, comment="Quantidade disponível do produto.")
    price = Column(Float, comment="Preço do produto.")
    low_stock_threshold = Column(Integer, comment="Limite de estoque baixo.")

class Pet(Base):
    '''Representa a tabela de pets no banco de dados.'''
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True, comment="Identificador único do pet.")
    name = Column(String, index=True, comment="Nome do pet.")
    breed = Column(String, index=True, comment="Raça do pet.")
    date_of_birth = Column(DateTime, index=True, comment="Data de nascimento do pet.")
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True, comment="Identificador único do cliente.")
   
class Vaccine(Base):
    '''Representa a tabela de vacinas no banco de dados.'''
    __tablename__ = "vaccines"

    id = Column(Integer,primary_key=True, index=True, comment="Identificador único da vacina.")
    pet_id = Column(Integer, ForeignKey("pets.id"), index=True, comment="Identificador único do pet.")
    vaccine_name = Column(String, index=True, comment="Nome da vacina.")
    date_of_application = Column(DateTime, index=True, comment="Data da aplicação da vacina.")


    