import os
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy import (
    Column, Integer, String, DECIMAL, Boolean, ForeignKey, create_engine
)

Base = declarative_base()

class Location(Base):
    __tablename__ = 'location'
    __table_args__ = {'schema': 'master'}

    id = Column(Integer, primary_key=True)
    external_id = Column(String(45))
    name = Column(String(45))
    short_name = Column(String(45))
    op_manager_id = Column(Integer)
    store_manager_id = Column(Integer)
    email = Column(String(45))
    phone = Column(String(45))
    address = Column(String(45))
    post_code = Column(String(45))
    city = Column(String(45))
    basware_approver = Column(String(45))
    display_name = Column(String(45))
    po_number = Column(String(45))
    department_id = Column(Integer, ForeignKey('master.department.id'))
    class_id = Column(Integer)
    active = Column(Boolean)
    basware_matching = Column(String(45))
    customer_id = Column(Integer)
    maraplan_location_name = Column(String(45))
    
    department = relationship('Department', backref='locations')


class Department(Base):
    __tablename__ = 'department'
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


# Create an engine using the environment variable 'DB_URL'
engine = create_engine(os.getenv('DB_URL', None))

# Create all tables in the Base metadata if they do not exist
Base.metadata.create_all(engine)

# Create a sessionmaker factory
SessionLocal = sessionmaker(bind=engine)