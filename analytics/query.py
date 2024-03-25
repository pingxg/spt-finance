import streamlit as st

from database.session import session_scope
from database.models import Department, Location, FinancialAccount,FinancialData

REPORT_TYPE = {
    'standard': 'std_rate',
    'adjusted': 'adj_rate',
    'adjusted_coef': 'adj_coef_rate',
}

@st.cache_data
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


@st.cache_data
def query_performance_overview_data(department='all', report_type='standard', begin=None, end=None):
    with session_scope() as session:
        query = session.query(FinancialData)
        if department != 'all':
            query = query.join(Location).filter(Location.department.has(name=department))
        if begin:
            query = query.filter(FinancialData.year >= begin.year, FinancialData.month >= begin.month)
        if end:
            query = query.filter(FinancialData.year <= end.year, FinancialData.month <= end.month)
        data = query.all()
        # Process and filter data according to report_type using REPORT_TYPE dict
        # This might involve aggregating data or applying specific rate columns
        return data
    
@st.cache_data
def query_cost_structure_data():
    ...

@st.cache_data
def prepare_performance_overview_data():
    ...

@st.cache_data
def prepare_cost_structure_data():

    ...


