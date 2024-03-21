import streamlit as st
from streamlit.logger import get_logger
from database.session import session_scope
from database.models import Department


LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.write("# Welcome to Streamlit! 👋")


if __name__ == "__main__":
    run()
    with session_scope() as session:
        department_names = [_.name for _ in session.query(Department).all()]

        st.write(department_names)
    
