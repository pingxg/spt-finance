from PIL import Image
import streamlit as st
from streamlit.logger import get_logger
from analytics.query import query_performance_overview_data

LOGGER = get_logger(__name__)



if __name__ == "__main__":
    st.set_page_config(
        page_title="Overview",
        page_icon=Image.open("assets/logo.ico"),
        layout='wide',
        initial_sidebar_state='auto',
    )
    st.write("# Financial Dashboard 📈")

    st.dataframe(query_performance_overview_data(department_name='food plant', start_str="2023-M01", end_str="2023-M04", report_type='standard'), use_container_width=True, hide_index=True)
