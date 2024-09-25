import os
import streamlit as st
import pandas as pd
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging for error tracking
logging.basicConfig(level=logging.INFO)

# NetSuite API Credentials
ACCOUNT_ID = os.getenv("NETSUITE_ACCOUNT_ID")
CONSUMER_KEY = os.getenv("NETSUITE_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("NETSUITE_CONSUMER_SECRET")
TOKEN_ID = os.getenv("NETSUITE_TOKEN_ID")
TOKEN_SECRET = os.getenv("NETSUITE_TOKEN_SECRET")

# Base URL for NetSuite REST API
BASE_URL = f"https://{ACCOUNT_ID.lower().replace('_', '-')}.suitetalk.api.netsuite.com/services/rest"


# Create an authenticated NetSuite session
def create_netsuite_session():
    try:
        session = OAuth1Session(
            client_key=CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=TOKEN_ID,
            resource_owner_secret=TOKEN_SECRET,
            realm=ACCOUNT_ID,
            signature_method="HMAC-SHA256",
        )
        return session
    except Exception as e:
        st.error("Failed to connect to NetSuite API.")
        logging.error(f"Error in create_netsuite_session: {e}")
        return None


@st.cache_data
def run_suiteql(query, limit=None, offset=None):
    session = create_netsuite_session()
    if not session:
        return None

    # Update URL with limit and offset parameters if provided
    url = f"{BASE_URL}/query/v1/suiteql"
    if limit is not None and offset is not None:
        url += f"?limit={limit}&offset={offset}"
    elif limit is not None:
        url += f"?limit={limit}"
    elif offset is not None:
        url += f"?offset={offset}"
    
    headers = {"Prefer": "transient", "Content-Type": "application/json"}
    payload = {"q": query}

    try:
        response = session.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error("Error fetching data from NetSuite.")
        logging.error(f"Error in run_suiteql: {e}")
        return None


# Retrieve balance sheet data
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



# Retrieve income statement data
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


# Convert the API response data into a Pandas DataFrame
def data_to_dataframe(data):
    if data and "items" in data:
        df = pd.json_normalize(data["items"])
        return df
    else:
        return pd.DataFrame()


# Display financial statement data in Streamlit
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


# Display charts for financial data
def display_charts(df, title):
    if not df.empty:
        st.subheader(f"{title} Chart")
        chart_data = df.set_index("account_name")["amount"]
        st.bar_chart(chart_data)



@st.cache_data
def get_test_data():
    query = f"""
    SELECT
        *
    FROM
        transaction

    """
    return run_suiteql(query, limit=100)


# @st.cache_data
# def get_test_data(start_date='2023-01-01', end_date='2023-12-31'):
#     query = f"""
#     SELECT
#         acc.name AS account_name,
#         acc.type AS account_type,
#         SUM(trx.amount) AS total_amount

#     FROM
#         transaction trx
#         INNER JOIN account acc ON trx.account = acc.id

#     WHERE
#         trx.recordtype IN ('invoice', 'journalentry')
#         AND trx.trandate BETWEEN TO_DATE('{start_date}', 'YYYY-MM-DD') AND TO_DATE('{end_date}', 'YYYY-MM-DD')

#     GROUP BY
#         acc.name, acc.type

#     ORDER BY
#         acc.type, acc.name
#     """
#     return run_suiteql(query)

# Main function for the Streamlit app
def main():
    st.set_page_config(page_title="Company Financial Dashboard", layout="wide")
    st.title("Company Financial Situation")
    st.write("Data pulled from NetSuite")

    # Improve the UI by using a dropdown for selecting periods
    periods = [
        "Q1 FY2023",
        "Q2 FY2023",
        "Q3 FY2023",
        "Q4 FY2023",
        "CURRENT_ACCOUNTING_PERIOD",
    ]
    selected_period = st.selectbox("Select Accounting Period", periods)

    # Add a loading indicator
    with st.spinner("Fetching data..."):
        # st.header("Balance Sheet")
        # balance_data = get_balance_sheet_data(selected_period)
        # balance_df = data_to_dataframe(balance_data)
        # display_financial_statement(balance_df, "Balance Sheet")
        # display_charts(balance_df, "Balance Sheet")

        # st.header("Income Statement")
        # income_data = get_income_statement_data(selected_period)
        # income_df = data_to_dataframe(income_data)
        # display_financial_statement(income_df, "Income Statement")
        # display_charts(income_df, "Income Statement")
        st.dataframe(data_to_dataframe(get_test_data()))

    # Provide additional information or help sections
    st.sidebar.title("Help & Information")
    st.sidebar.write(
        "This dashboard displays your company's financial information. Select an accounting period from the dropdown, and the data will update accordingly."
    )

    st.sidebar.write(
        "For more detailed analysis, you can download the financial data as CSV files by clicking the buttons provided under each section."
    )


# Run the app
if __name__ == "__main__":
    main()
