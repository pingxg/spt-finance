import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import logging
from analytics.data_processing import (
    get_balance_sheet_data,
    get_income_statement_data,
    data_to_dataframe,
    display_financial_statement,
    display_charts,
)

# Load environment variables from .env file
load_dotenv()

# Set up logging for error tracking
logging.basicConfig(level=logging.INFO)

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
        st.header("Balance Sheet")
        balance_data = get_balance_sheet_data(selected_period)
        balance_df = data_to_dataframe(balance_data)
        display_financial_statement(balance_df, "Balance Sheet")
        display_charts(balance_df, "Balance Sheet")

        st.header("Income Statement")
        income_data = get_income_statement_data(selected_period)
        income_df = data_to_dataframe(income_data)
        display_financial_statement(income_df, "Income Statement")
        display_charts(income_df, "Income Statement")

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
