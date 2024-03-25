from PIL import Image
import streamlit as st
from streamlit.logger import get_logger
from database.session import session_scope
from database.models import Department, Location, FinancialAccount
from analytics.query import query_unique_timeframes, query_performance_overview_data

LOGGER = get_logger(__name__)



if __name__ == "__main__":
    st.set_page_config(
        page_title="Overview",
        page_icon=Image.open("assets/logo.ico"),
        layout='wide',
        initial_sidebar_state='auto',
    )
    st.write("# Financial Dashboard 📈")

    st.write(query_performance_overview_data(department_name='food plant', start_str="2024", end_str="2024", report_type='standard'))
