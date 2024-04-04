import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, and_, or_, func, extract, desc
from datetime import datetime
from database.session import session_scope
from database.models import Department, Location, FinancialAccount, FinancialData, SalesData

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
    df['year_month'] = df['year'].astype(str) + '-M' + df['month'].apply(lambda x: f'{x:02d}')
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
def query_performance_overview_data(department_name=None, report_type='standard', start_str=None, end_str=None, timeframe="quarter", custom_adjustment=True, split_office_cost=False):
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
            if not split_office_cost:
                query = query.filter(Location.department.has(name=department_name))
            else:
                # don't filter the department here
                pass
        
        if start_str is not None:
            if timeframe == "quarter":
                year, quarter = map(int, start_str.split('-Q'))
                query = query.filter(
                    (FinancialData.year > year) | 
                    ((FinancialData.year == year) & 
                    (((FinancialData.month - 1) // 3 + 1) >= quarter))
                )
            elif timeframe == "month":
                year, month = map(int, start_str.split('-M'))
                query = query.filter(
                    (FinancialData.year > year) | 
                    ((FinancialData.year == year) & 
                    (FinancialData.month >= month))
                )
            else:  # Assuming start_str is just a year here
                query = query.filter(FinancialData.year >= int(start_str))
        
        if end_str is not None:
            if timeframe == "quarter":
                year, quarter = map(int, end_str.split('-Q'))
                query = query.filter(
                    (FinancialData.year < year) | 
                    ((FinancialData.year == year) & 
                    (((FinancialData.month - 1) // 3 + 1) <= quarter))
                )
            elif timeframe == "month":
                year, month = map(int, end_str.split('-M'))
                query = query.filter(
                    (FinancialData.year < year) | 
                    ((FinancialData.year == year) & 
                    (FinancialData.month <= month))
                )
            else:  # Assuming end_str is just a year here
                query = query.filter(FinancialData.year <= int(end_str))

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
    result_df = generate_period_str(df, timeframe)
    if custom_adjustment:
        result_df = financial_data_custom_adjustment(result_df)
    if split_office_cost:
        result_df = office_cost_adjustment(result_df)
    return result_df



@st.cache_data(ttl=600)
def query_sales_data(department_name=None, start_str=None, end_str=None, timeframe="quarter"):
    timeframe = timeframe.lower()
    if 'q' in start_str.lower() or 'q' in end_str.lower():
        timeframe = 'quarter'
    elif 'm' in start_str.lower() or 'm' in end_str.lower():
        timeframe = 'month'
    else:
        timeframe = 'year'

    with session_scope() as session:
        query = session.query(
            SalesData.date, 
            SalesData.amount,
            SalesData.product_catagory,
            SalesData.location_internal_id,
            Location.short_name.label('sushibar_name'),
            Department.name.label('department_name'),
        ).join(
            Location, SalesData.location_internal_id == Location.id
        ).join(
            Department, Location.department_id == Department.id
        )

        if department_name is not None:
            query = query.filter(Location.department.has(name=department_name))
        
        # Assuming start_str and end_str are provided in the format "YYYY" for year, "YYYY-QX" for quarters,
        # and "YYYY-MM" for months, you can split these strings to extract the numerical values for year, quarter, and month.

        if start_str is not None:
            if timeframe == "quarter":
                year, quarter = map(int, start_str.split('-Q'))
                query = query.filter(
                    (extract('year', SalesData.date) > year) | 
                    ((extract('year', SalesData.date) == year) & 
                    (((extract('month', SalesData.date) - 1) // 3 + 1) >= quarter))
                )
            elif timeframe == "month":
                year, month = map(int, start_str.split('-M'))
                query = query.filter(
                    (extract('year', SalesData.date) > year) | 
                    ((extract('year', SalesData.date) == year) & 
                    (extract('month', SalesData.date) >= month))
                )
            else:  # Assuming start_str is just a year here
                query = query.filter(extract('year', SalesData.date) >= int(start_str))
        
        if end_str is not None:
            if timeframe == "quarter":
                year, quarter = map(int, end_str.split('-Q'))
                query = query.filter(
                    (extract('year', SalesData.date) < year) | 
                    ((extract('year', SalesData.date) == year) & 
                    (((extract('month', SalesData.date) - 1) // 3 + 1) <= quarter))
                )
            elif timeframe == "month":
                year, month = map(int, end_str.split('-M'))
                query = query.filter(
                    (extract('year', SalesData.date) < year) | 
                    ((extract('year', SalesData.date) == year) & 
                    (extract('month', SalesData.date) <= month))
                )
            else:  # Assuming end_str is just a year here
                query = query.filter(extract('year', SalesData.date) <= int(end_str))

        results = query.all()
        
        results_data = [{
            'date': date,
            'amount': amount,
            'product_category': product_catagory,
            'location_id': location_internal_id,
            'sushibar_name': sushibar_name,
            'department_name': department_name,
        } for date, amount, product_catagory, location_internal_id, sushibar_name, department_name in results]

    df = pd.DataFrame(results_data)
    # result_df = generate_period_str(df, timeframe)

    
    return df


@st.cache_data(ttl=600)
def financial_data_custom_adjustment(df):
    df = df.copy()
    return df

@st.cache_data(ttl=600)
def office_cost_adjustment(df):
    df = df.copy()
    return df


@st.cache_data(ttl=600)
def prepare_performance_overview_data(df, denominator="sales"):
    df = df.copy()
    df['amount_calc'] = df['amount'] * df['rate']
    df_grouped = df.groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped_sales = df.loc[df['account_type'].isin(["sales", "other income"])].groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped_material = df.loc[df['account_type']=="material"].groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped_staff = df.loc[df['account_type']=="staff"].groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped_other = df.loc[df['account_type']=="other cost"].groupby(['period'])['amount_calc'].sum().reset_index().sort_values(by=['period'], kind='mergesort', ascending=[True])
    df_grouped = pd.merge(df_grouped, df_grouped_sales, on="period", validate="1:1",suffixes=(None,'_sales'),how='left')
    df_grouped = pd.merge(df_grouped, df_grouped_material, on="period", validate="1:1",how='left',suffixes=(None,'_material'))
    df_grouped = pd.merge(df_grouped, df_grouped_staff, on="period", validate="1:1",how='left',suffixes=(None,'_staff'))
    df_grouped = pd.merge(df_grouped, df_grouped_other, on="period", validate="1:1",how='left',suffixes=(None,'_other'))
    if denominator == "sales":
        df_grouped['material_rate'] = (df_grouped['amount_calc_material']/df_grouped['amount_calc_sales']).abs()
        df_grouped['staff_rate']= (df_grouped['amount_calc_staff']/df_grouped['amount_calc_sales']).abs()
        df_grouped['other_rate']= (df_grouped['amount_calc_other']/df_grouped['amount_calc_sales']).abs()
    elif denominator == "costs":
        df_grouped['material_rate'] = (df_grouped['amount_calc_material']/(df_grouped['amount_calc_material']+df_grouped['amount_calc_staff']+df_grouped['amount_calc_other'])).abs()
        df_grouped['staff_rate']= (df_grouped['amount_calc_staff']/(df_grouped['amount_calc_material']+df_grouped['amount_calc_staff']+df_grouped['amount_calc_other'])).abs()
        df_grouped['other_rate']= (df_grouped['amount_calc_other']/(df_grouped['amount_calc_material']+df_grouped['amount_calc_staff']+df_grouped['amount_calc_other'])).abs()
    df_grouped['profit_rate']= (df_grouped['amount_calc']/df_grouped['amount_calc_sales'])
    df_grouped.fillna(0,inplace=True)
    return df_grouped

@st.cache_data(ttl=600)
def prepare_turnover_structure_data(df, department_name=None):
    df = df.copy()
    df['amount_calc'] = df['amount'] * df['rate']
    if department_name is None:
        df_grouped_sales = df.loc[df['account_type'].isin(["sales", "other income"])]\
            .groupby(['period', 'department_name'])['amount_calc']\
            .sum()\
            .reset_index()\
            .sort_values(by=['period','amount_calc'], kind='mergesort', ascending=[True, False])
        
        pivot_df = df_grouped_sales.pivot_table(index='period', columns='department_name', values='amount_calc', aggfunc='sum')
    else:
        df_grouped_sales = df.loc[(df['account_type'].isin(["sales"])) & (df['department_name']==department_name)]\
            .groupby(['period', 'account_name'])['amount_calc'].sum()\
            .reset_index()\
            .sort_values(by=['period','amount_calc'], kind='mergesort', ascending=[True, False])
        pivot_df = df_grouped_sales.pivot_table(index='period', columns='account_name', values='amount_calc', aggfunc='sum')

    # Pivoting the data with 'period' as index, 'location' as columns, and 'amount' as values
    pivot_df.reset_index(inplace=True)  # Resetting the index if you want 'period' as a column
    return pivot_df

@st.cache_data(ttl=600)
def prepare_sales_data(df):
    df = df.copy()
    df['amount_calc'] = df['amount'] * df['rate']


@st.cache_data(ttl=600)
def prepare_cost_structure_breakdown(df, department_name=None):
    df = df.copy()
    if department_name is not None:
        df = df.loc[df['department_name']==department_name]
    result_df = prepare_performance_overview_data(df, denominator="sales")
    return result_df


@st.cache_data(ttl=600)
def prepare_cost_structure_cumulative(df, department_name=None):
    results = {}
    df = df.copy()
    results['departments'] = sorted(df['department_name'].unique().tolist())
    df['amount_calc'] = df['amount'] * df['rate']
    if department_name is None:
        df_costs = df.loc[~df['account_type'].isin(["sales", "other income"])]
    else:
        df_costs = df.loc[~df['account_type'].isin(["sales", "other income"])]
        df_costs = df.loc[df['department_name']==department_name]
        
    results['total_cost'] = float(df_costs['amount_calc'].sum())
    results['total_material_cost'] = float(df_costs[df_costs['account_type'] == 'material']['amount_calc'].sum())
    results['total_staff_cost'] = float(df_costs[df_costs['account_type'] == 'staff']['amount_calc'].sum())
    results['total_other_cost'] = float(df_costs[df_costs['account_type'] == 'other cost']['amount_calc'].sum())
    
    results['total_sushibar_cost'] = float(df_costs[df_costs['department_name'] == 'Food Kiosk Sushibar']['amount_calc'].sum())
    results['total_sushibar_material'] = float(df_costs[(df_costs['account_type'] == 'material') & (df_costs['department_name'] == "Food Kiosk Sushibar")]['amount_calc'].sum())
    results['total_sushibar_staff'] = float(df_costs[(df_costs['account_type'] == 'staff') & (df_costs['department_name'] == "Food Kiosk Sushibar")]['amount_calc'].sum())
    results['total_sushibar_other'] = float(df_costs[(df_costs['account_type'] == 'other cost') & (df_costs['department_name'] == "Food Kiosk Sushibar")]['amount_calc'].sum())

    results['total_plant_cost'] = float(df_costs[df_costs['department_name'] == 'Food Plant']['amount_calc'].sum())
    results['total_plant_material'] = float(df_costs[(df_costs['account_type'] == 'material') & (df_costs['department_name'] == "Food Plant")]['amount_calc'].sum())
    results['total_plant_staff'] = float(df_costs[(df_costs['account_type'] == 'staff') & (df_costs['department_name'] == "Food Plant")]['amount_calc'].sum())
    results['total_plant_other'] = float(df_costs[(df_costs['account_type'] == 'other cost') & (df_costs['department_name'] == "Food Plant")]['amount_calc'].sum())

    results['total_restaurant_cost'] = float(df_costs[df_costs['department_name'] == 'Restaurant']['amount_calc'].sum())
    results['total_restaurant_material'] = float(df_costs[(df_costs['account_type'] == 'material') & (df_costs['department_name'] == "Restaurant")]['amount_calc'].sum())
    results['total_restaurant_staff'] = float(df_costs[(df_costs['account_type'] == 'staff') & (df_costs['department_name'] == "Restaurant")]['amount_calc'].sum())
    results['total_restaurant_other'] = float(df_costs[(df_costs['account_type'] == 'other cost') & (df_costs['department_name'] == "Restaurant")]['amount_calc'].sum())

    results['total_office_cost'] = float(df_costs[df_costs['department_name'] == 'Head Office']['amount_calc'].sum())
    results['total_office_material'] = float(df_costs[(df_costs['account_type'] == 'material') & (df_costs['department_name'] == "Head Office")]['amount_calc'].sum())
    results['total_office_staff'] = float(df_costs[(df_costs['account_type'] == 'staff') & (df_costs['department_name'] == "Head Office")]['amount_calc'].sum())
    results['total_office_other'] = float(df_costs[(df_costs['account_type'] == 'other cost') & (df_costs['department_name'] == "Head Office")]['amount_calc'].sum())
    return results



@st.cache_data(ttl=600)
def prepare_cost_structure_cumulative_icicle(df):
    df = df.copy()
    df['amount_calc'] = df['amount']
    df_costs = df.loc[~df['account_type'].isin(["sales", "other income"])]
    df_costs = df_costs.loc[df_costs['amount_calc']>=0]
    # Function to extract initials
    def get_initials(s):
        # return ''.join(word[0] for word in s.split()).upper()
        return s.split()[-1][0].lower()

    # Applying the function to the 'department_name' column to create a new column 'dept_initials'
    df_costs['dept_initials'] = df_costs['department_name'].apply(get_initials)
    df_costs['account_type'] = df_costs['account_type'].str.capitalize()
    
    # Concatenating the initials with 'account_type' and 'account_name'
    df_costs['account_type'] = df_costs['account_type'] + '-' + df_costs['dept_initials']
    df_costs['account_name'] = df_costs['account_name'] + '-' + df_costs['dept_initials']

    df_costs = df_costs.groupby(['department_name', 'account_type', 'account_name'])
    df_costs = df_costs['amount_calc'].sum().reset_index()

    levels = ['account_name', 'account_type', 'department_name'] # levels used for the hierarchical chart
    value_column = 'amount_calc'

    def build_hierarchical_dataframe(df, levels, value_column):
        """
        Build a hierarchy of levels for Icicle charts.

        Levels are given starting from the bottom to the top of the hierarchy,
        ie the last level corresponds to the root.
        """
        df_all_trees = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
        for i, level in enumerate(levels):
            df_tree = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
            dfg = df.groupby(levels[i:]).sum()
            dfg = dfg.reset_index()
            df_tree['id'] = dfg[level].copy()
            if i < len(levels) - 1:
                df_tree['parent'] = dfg[levels[i+1]].copy()
            else:
                df_tree['parent'] = 'total'
            df_tree['value'] = dfg[value_column]
            df_tree['color'] = dfg[value_column]
            df_all_trees = pd.concat([df_all_trees, df_tree], ignore_index=True)
        total_row = pd.DataFrame([{
            'id': 'total',
            'parent': '',
            'value': df[value_column].sum(),
            'color': df[value_column].sum()
        }])
        df_all_trees = pd.concat([df_all_trees, total_row], ignore_index=True)
        return df_all_trees

    df_all_trees = build_hierarchical_dataframe(df_costs, levels, value_column)

    return df_all_trees