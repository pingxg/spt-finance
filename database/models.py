import os
from dotenv import load_dotenv

from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import (
    Column, Integer, String, DECIMAL, Boolean, ForeignKey, create_engine, DATE, DATETIME
)
load_dotenv()

Base = declarative_base()


class SalesData(Base):
    __tablename__ = 'sales_data'
    __table_args__ = {'schema': 'data'}

    id = Column(Integer, primary_key=True)
    date = Column(DATE)
    product_internal_id = Column(Integer)
    quantity = Column(DECIMAL)
    amount = Column(DECIMAL)
    unit = Column(String)
    product_catagory = Column(String)
    location_internal_id = Column(Integer, ForeignKey('master.location.id'))
    upload_time = Column(DATETIME)
    store_name = Column(String)

    location = relationship('Location', backref='locations')

class Location(Base):
    __tablename__ = 'location'
    __table_args__ = {'schema': 'master'}

    id = Column(Integer, primary_key=True)
    name = Column(String(45))
    store_name = Column(String(45))
    short_name = Column(String(45))
    status = Column(String(45))
    active = Column(Boolean)
    department_id = Column(Integer, ForeignKey('master.department.id'))
    class_id = Column(Integer)
    basware_matching = Column(String(45))
    basware_approver = Column(String(45))
    customer_id = Column(Integer)
    op_manager_id = Column(Integer, ForeignKey('master.manager.id'))
    store_manager_id = Column(Integer, ForeignKey('master.manager.id'))
    po_number = Column(String(45))
    email = Column(String(45))
    phone = Column(String(45))
    address = Column(String(45))
    post_code = Column(String(45))
    city = Column(String(45))
    country = Column(String(45))
    maraplan_location_name = Column(String(45))
    
    department = relationship('Department', backref='locations')


class Manager(Base):
    __tablename__ = 'manager'
    __table_args__ = {'schema': 'master'}
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    phone = Column(String(45))
    email = Column(String(45))

class Department(Base):
    __tablename__ = 'department'
    __table_args__ = {'schema': 'master'}

    id = Column(Integer, primary_key=True)
    external_id = Column(String(45))
    name = Column(String(45))
    active = Column(Boolean)

class Class(Base):
    __tablename__ = 'class'
    __table_args__ = {'schema': 'master'}

    id = Column(Integer, primary_key=True)
    external_id = Column(String(45))
    name = Column(String(45))
    active = Column(Boolean)


class FinancialAccount(Base):
    __tablename__ = 'financial_account'
    __table_args__ = {'schema': 'master'}

    id = Column(Integer, primary_key=True)
    account_id = Column(String(7))
    account_name = Column(String(80))
    account_type = Column(String(20))
    std_rate = Column(DECIMAL(10, 2))
    adj_rate = Column(DECIMAL(10, 2))
    adj_coef_rate = Column(DECIMAL(10, 2))

    financial_data = relationship('FinancialData', back_populates='financial_account')


class FinancialData(Base):
    __tablename__ = 'financial_data'
    __table_args__ = {'schema': 'data'}

    id = Column(Integer, primary_key=True)
    account_id = Column(String(7), ForeignKey('master.financial_account.account_id'))
    amount = Column(DECIMAL(15, 2))
    month = Column(Integer)
    year = Column(Integer)
    location_id = Column(Integer, ForeignKey('master.location.id'))

    financial_account = relationship('FinancialAccount', back_populates='financial_data')


class SalmonOrders(Base):
    __tablename__ = 'salmon_orders'
    __table_args__ = {'schema': 'data'}

    id = Column(Integer, primary_key=True)
    customer = Column(String(45))
    date = Column(DECIMAL(15, 2))
    product = Column(String(45))
    price = Column(DECIMAL(8, 4))
    quantity = Column(DECIMAL(6, 2))
    fish_size = Column(String(45))
    entry_time = Column(DATETIME)
    note = Column(String(120))


class SalmonOrderWeight(Base):
    __tablename__ = 'salmon_order_weight'
    __table_args__ = {'schema': 'data'}

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('data.salmon_orders.id'))
    quantity = Column(DECIMAL(6, 2))
    product_time = Column(DATETIME)
    batch_number = Column(Integer)



# Create an engine using the environment variable 'MYSQL_URL'
engine = create_engine(os.getenv('MYSQL_URL', None))

# Create all tables in the Base metadata if they do not exist
Base.metadata.create_all(engine)

# Create a sessionmaker factory
SessionLocal = sessionmaker(bind=engine)