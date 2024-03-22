import streamlit as st
from streamlit.logger import get_logger
from database.session import session_scope
from database.models import Department, Location, FinancialAccount


LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Overview",
    )
    st.write("# Spartao Financial Dashboard 📈")


if __name__ == "__main__":
    run()
    with session_scope() as session:
        department_names = [_.name for _ in session.query(Department).all()]
        st.write(department_names)
        st.write([(_.account_id, _.account_name, _.account_type) for _ in session.query(FinancialAccount).all()])