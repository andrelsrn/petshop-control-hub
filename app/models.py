from sqlalchemy import (Column, Integer, String, Float, DateTime,
                        Boolean, ForeignKey, func)
from app.core.database import Base
from sqlalchemy.orm import relationship


class Customer(Base):
    '''Representa um cliente (tutor de pet).'''
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    is_active = Column(Boolean, default=True, nullable=False)
    
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    address = Column(String(255))
    cpf = Column(String(11), unique=True, index=True, nullable=False)

    pets = relationship("Pet", back_populates="owner", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")

class Pet(Base):
    '''Representa um pet, pertecente a um cliente.'''
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    name = Column(String(100), nullable=False)
    breed = Column(String(100), nullable=False)
    species = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime(timezone=True))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    owner = relationship("Customer", back_populates="pets")
    bookings = relationship("Booking", back_populates="pet", cascade="all, delete-orphan")
    vaccines = relationship("Vaccine", back_populates="pet", cascade="all, delete-orphan")


class Employee(Base):
    '''Representa um funcionário do PetShop.'''
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    name = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    phone = Column(String(20))
    cpf = Column(String(11), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


    bookings = relationship("Booking", back_populates="employee")

class Booking(Base):
    '''Representa um agendamento de serviço para um pet com um funcionário específico.'''
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    service_name = Column(String(100), nullable=False)
    scheduled_time = Column(DateTime(timezone=True), index=True, nullable=False)
    delivery = Column(Boolean, default=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    
    pet = relationship("Pet", back_populates="bookings")
    employee = relationship("Employee", back_populates="bookings")
    
class Inventory(Base):
    '''Representa um produto no inventário do PetShop.'''
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product_name = Column(String(100), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    low_stock_threshold = Column(Integer, nullable=False, default=5)

    sale_items = relationship("Sale", back_populates="product")

class Sale(Base):
    '''Representa uma linha de venda com produto para um cliente.'''
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    quantity = Column(Integer, nullable=False)
    total_value = Column(Float, nullable=False)
    product_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False) 
    
    is_active = Column(Boolean, default=True, nullable=False)


    product = relationship("Inventory", back_populates="sale_items")
    customer = relationship("Customer", back_populates="sales")

class Vaccine(Base):
    '''Representa uma vacina aplicada a um pet.'''
    __tablename__ = "vaccines"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vaccine_name = Column(String(100), nullable=False)
    date_of_application = Column(DateTime(timezone=True), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)

    pet = relationship("Pet", back_populates="vaccines")