import streamlit as st
import pandas as pd
from utils.netsuite_api import run_suiteql

@st.cache_data
def get_balance_sheet_data(period):
    query = f"""
    SELECT
        acct.name AS account_name,
        acct.number AS account_number,
        SUM(trx.amount) AS amount
    FROM
        transaction trx
    JOIN
        account acct ON (trx.account = acct.id)
    WHERE
        acct.type IN (
            'Bank', 'AccountsReceivable', 'OtherCurrentAsset', 'FixedAsset',
            'OtherAsset', 'AccountsPayable', 'CreditCard', 'OtherCurrentLiability',
            'LongTermLiability', 'Equity'
        )
        AND trx.postingperiod = '{period}'
    GROUP BY
        acct.name, acct.number
    ORDER BY
        acct.number
    """
    return run_suiteql(query)

@st.cache_data
def get_income_statement_data(period):
    query = f"""
    SELECT
        acct.name AS account_name,
        acct.number AS account_number,
        SUM(trx.amount) AS amount
    FROM
        transaction trx
    JOIN
        account acct ON (trx.account = acct.id)
    WHERE
        acct.type IN (
            'Income', 'Expense', 'OtherIncome', 'OtherExpense'
        )
        AND trx.postingperiod = '{period}'
    GROUP BY
        acct.name, acct.number
    ORDER BY
        acct.number
    """
    return run_suiteql(query)

def data_to_dataframe(data):
    if data and "items" in data:
        df = pd.json_normalize(data["items"])
        return df
    else:
        return pd.DataFrame()

def display_financial_statement(df, title):
    if not df.empty:
        df["amount"] = df["amount"].astype(float)
        total = df["amount"].sum()
        st.subheader(f"{title} (Total: ${total:,.2f})")
        st.dataframe(df.style.format({"amount": "${:,.2f}"}))

        # Add export button to download as CSV
        st.download_button(
            label="Download as CSV",
            data=df.to_csv().encode("utf-8"),
            file_name=f'{title.lower().replace(" ", "_")}.csv',
            mime="text/csv",
        )
    else:
        st.warning(f"No data available for {title}.")

def display_charts(df, title):
    if not df.empty:
        st.subheader(f"{title} Chart")
        chart_data = df.set_index("account_name")["amount"]
        st.bar_chart(chart_data)

# New functions for basic testing
@st.cache_data
def get_test_data():
    query = """
    SELECT 
        id, 
        trandate, 
        amount
    FROM 
        transaction
    LIMIT 10
    """
    return run_suiteql(query)

def display_test_data(df):
    if not df.empty:
        st.subheader("Test Data")
        st.dataframe(df)
    else:
        st.warning("No test data available.")

@st.cache_data
def get_simple_account_data():
    query = """
    SELECT 
        id, 
        acctname, 
        accttype
    FROM 
        account
    LIMIT 5
    """
    return run_suiteql(query)

def display_simple_account_data(df):
    if not df.empty:
        st.subheader("Simple Account Data")
        st.dataframe(df)
    else:
        st.warning("No account data available.")