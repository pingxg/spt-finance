from PIL import Image
import streamlit as st
from streamlit.logger import get_logger
from database.session import session_scope
from database.models import Department, Location, FinancialAccount
from analytics.query import query_unique_timeframes

LOGGER = get_logger(__name__)



if __name__ == "__main__":
    st.set_page_config(
        page_title="Overview",
        page_icon=Image.open("assets/logo.ico"),
        layout='wide',
        initial_sidebar_state='auto'
    )
    st.write("# Financial Dashboard 📈")

    st.write(query_unique_timeframes())
    st.write(query_unique_timeframes('month'))
    st.write(query_unique_timeframes('year'))
