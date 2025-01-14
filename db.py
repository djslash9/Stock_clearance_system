from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

# Product Item Model (make sure this is defined)
class ProductItem(Base):
    __tablename__ = 'product_items'
    item_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    purchase_price = Column(Float)
    selling_price = Column(Float)
    stock_shop = Column(Integer)
    stock_warehouse = Column(Integer)

# Customer Model
class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact_info = Column(String)
    purchase_history = relationship("Sale", back_populates="customer")

# Employee Model
class Employee(Base):
    __tablename__ = 'employees'
    employee_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    designation = Column(String)
    salary = Column(Float)
    commission_rate = Column(Float)
    sales = relationship("Sale", back_populates="salesperson")

# Sales Model
class Sale(Base):
    __tablename__ = 'sales'
    sale_id = Column(Integer, primary_key=True)
    sale_date = Column(Date)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    salesperson_id = Column(Integer, ForeignKey('employees.employee_id'))
    item_id = Column(Integer, ForeignKey('product_items.item_id'))
    quantity_sold = Column(Integer)
    sales_price = Column(Float)
    total_sale_amount = Column(Float)
    commission_earned = Column(Float)
    
    customer = relationship("Customer", back_populates="purchase_history")
    salesperson = relationship("Employee", back_populates="sales")
    item = relationship("ProductItem")

# Database connection
engine = create_engine('sqlite:///shop_database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()