import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import joinedload
from datetime import datetime
from database.session import session_scope
from database.models import Department, Location, FinancialAccount, FinancialData

REPORT_TYPE = {
    'standard': 'std_rate',
    'adjusted': 'adj_rate',
    'adjusted_coef': 'adj_coef_rate',
}

@st.cache_data(ttl=600)
def query_unique_timeframes(timeframe='quarter'):
    timeframe = timeframe.lower()
    with session_scope() as session:
        if timeframe == 'quarter':
            results = session.query(FinancialData.year, FinancialData.month).distinct().all()
            quarters = set(f"{year}-Q{(month - 1) // 3 + 1}" for year, month in results)
            # return sorted(quarters)
            return [i for i in sorted(quarters)]
        elif timeframe == 'month':
            results = session.query(FinancialData.year, FinancialData.month).distinct().all()
            months = set(f"{year}-M{str(month).zfill(2)}" for year, month in results)
            return [i for i in sorted(months)]
        elif timeframe == 'year':
            results = session.query(FinancialData.year).distinct().all()
            years = set(results)
            return [str(i[0]) for i in sorted(years)]

@st.cache_data(ttl=600)
def generate_period_str(df, timeframe):
    if timeframe == 'year':
        # Convert year to string directly.
        df['period'] = df['year'].astype(str)
    elif timeframe == 'quarter':
        # Calculate quarter from month and format.
        df['period'] = df['year'].astype(str) + '-Q' + ((df['month'] - 1) // 3 + 1).astype(str)
    elif timeframe == 'month':
        # Format as year-month with zero-filled month.
        df['period'] = df['year'].astype(str) + '-M' + df['month'].apply(lambda x: f'{x:02d}')
    else:
        raise ValueError("Invalid timeframe specified. Use 'year', 'quarter', or 'month'.")
    df = df.drop(columns=['year', 'month'])
    return df


def format_date_by_timeframe(timeframe):
    current_date = datetime.now()

    if timeframe.lower() == 'month':
        # Format as 'YYYY-M01'
        return current_date.strftime('%Y-M%m')
    elif timeframe.lower() == 'quarter':
        # Calculate the quarter
        quarter = (current_date.month - 1) // 3 + 1
        # Format as 'YYYY-Q1'
        return f"{current_date.year}-Q{quarter}"
    elif timeframe.lower() == 'year':
        # Format as 'YYYY'
        return current_date.strftime('%Y')
    else:
        raise ValueError("Unsupported timeframe specified.")


@st.cache_data(ttl=600)
def query_performance_overview_data(department_name=None, report_type='standard', start_str=None, end_str=None, timeframe="quarter"):
    report_type = report_type.lower()
    timeframe = timeframe.lower()
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
    df = pd.DataFrame(results_data)
    df_with_period_str = generate_period_str(df, timeframe)
    return df_with_period_str

@st.cache_data(ttl=600)
def query_cost_structure_data():
    ...

@st.cache_data(ttl=600)
def prepare_performance_overview_data(department_name=None, report_type='standard', start_str=None, end_str=None, timeframe="quarter"):
    df = query_performance_overview_data(department_name=department_name, report_type=report_type, start_str=start_str, end_str=end_str, timeframe=timeframe)
    df['amount_calc'] = df['amount'] * df['rate']
    df_grouped = df.groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped_sales = df.loc[df['account_type']=="sales"].groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped_material = df.loc[df['account_type']=="material"].groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped_staff = df.loc[df['account_type']=="staff"].groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped_other = df.loc[df['account_type']=="other cost"].groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped = pd.merge(df_grouped, df_grouped_sales, on="period", validate="1:1",suffixes=(None,'_sales'),how='left')
    df_grouped = pd.merge(df_grouped, df_grouped_material, on="period", validate="1:1",how='left',suffixes=(None,'_material'))
    df_grouped = pd.merge(df_grouped, df_grouped_staff, on="period", validate="1:1",how='left',suffixes=(None,'_staff'))
    df_grouped = pd.merge(df_grouped, df_grouped_other, on="period", validate="1:1",how='left',suffixes=(None,'_other'))
    df_grouped['material_rate'] = (df_grouped['amount_calc_material']/df_grouped['amount_calc_sales']).abs()
    df_grouped['staff_rate']= (df_grouped['amount_calc_staff']/df_grouped['amount_calc_sales']).abs()
    df_grouped['other_rate']= (df_grouped['amount_calc_other']/df_grouped['amount_calc_sales']).abs()
    df_grouped['profit_rate']= (df_grouped['amount_calc']/df_grouped['amount_calc_sales'])
    df_grouped.fillna(0,inplace=True)
    return df_grouped

@st.cache_data(ttl=600)
def prepare_cost_structure_data():
    ...


