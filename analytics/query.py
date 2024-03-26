import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import joinedload

from database.session import session_scope
from database.models import Department, Location, FinancialAccount, FinancialData

REPORT_TYPE = {
    'standard': 'std_rate',
    'adjusted': 'adj_rate',
    'adjusted_coef': 'adj_coef_rate',
}

@st.cache_data(ttl=600)
def query_unique_timeframes(timeframe='quarter'):
    with session_scope() as session:
        if timeframe == 'quarter':
            results = session.query(FinancialData.year, FinancialData.month).distinct().all()
            quarters = set(f"{year}-Q{(month - 1) // 3 + 1}" for year, month in results)
            return sorted(quarters)
        elif timeframe == 'month':
            results = session.query(FinancialData.year, FinancialData.month).distinct().all()
            months = set(f"{year}-M{str(month).zfill(2)}" for year, month in results)
            return sorted(months)
        elif timeframe == 'year':
            results = session.query(FinancialData.year).distinct().all()
            years = set(results)
            return sorted(years)


@st.cache_data(ttl=600)
def query_performance_overview_data(department_name=None, report_type='standard', start_str=None, end_str=None, timeframe="quarter"):
    if 'q' in start_str.lower() or 'q' in end_str.lower():
        timeframe = 'quarter'
    elif 'm' in start_str.lower() or 'm' in end_str.lower():
        timeframe = 'month'
    else:
        timeframe = 'year'
    
    with session_scope() as session:
        query = session.query(
            FinancialData.year, 
            FinancialData.month, 
            FinancialData.location_id,
            Location.short_name.label('location_name'),
            Department.name.label('department_name'),
            FinancialData.account_id, 
            FinancialData.amount,
            FinancialAccount.account_name,
            FinancialAccount.account_type
        ).join(
            FinancialAccount, FinancialData.account_id == FinancialAccount.account_id
        ).join(
            Location, FinancialData.location_id == Location.id
        ).join(
            Department, Location.department_id == Department.id
        )
        if report_type is not None:
            ratio_column = REPORT_TYPE[report_type]
            additional_column = getattr(FinancialAccount, ratio_column, None)
            
            if additional_column is not None:
                query = query.add_columns(additional_column)
            else:
                raise ValueError(f"Column '{ratio_column}' not found in FinancialAccount model.")
    
        if department_name is not None:
            # query = query.join(Location).filter(Location.department.has(name=department_name))
            query = query.filter(Location.department.has(name=department_name))
        
        if start_str is not None:
            if timeframe == "quarter":
                query = query.filter(func.concat(FinancialData.year, '-Q', ((FinancialData.month - 1) // 3 + 1)) >= start_str)
            elif timeframe == "month":
                query = query.filter(func.concat(FinancialData.year, '-M', func.lpad(FinancialData.month, 2, '0')) >= start_str)
            else:
                query = query.filter(FinancialData.year >= start_str)
        
        if end_str is not None:
            if timeframe == "quarter":
                query = query.filter(func.concat(FinancialData.year, '-Q', ((FinancialData.month - 1) // 3 + 1)) <= end_str)
            elif timeframe == "month":
                query = query.filter(func.concat(FinancialData.year, '-M', func.lpad(FinancialData.month, 2, '0')) <= end_str)
            else:
                query = query.filter(FinancialData.year <= end_str)
        
        results = query.all()
        
        results_data = [{
            'year': year,
            'month': month,
            'location_id': location_id,
            'location_name': location_name,
            'department_name': department_name,
            'account_id': account_id,
            'amount': amount,
            'account_name': account_name,
            'account_type': account_type,
            'rate': ratio_column,
        } for year, month, location_id, location_name, department_name, account_id, amount, account_name, account_type, ratio_column in results]
    
    return pd.DataFrame(results_data)

@st.cache_data(ttl=600)
def query_cost_structure_data():
    ...

@st.cache_data(ttl=600)
def prepare_performance_overview_data():
    ...

@st.cache_data(ttl=600)
def prepare_cost_structure_data():
    ...


