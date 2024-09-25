
from PIL import Image
import streamlit as st
from analytics.query import *
from visuals.graphs import *


st.set_page_config(
    page_title="Office",
    page_icon=Image.open("assets/logo.ico"),
    layout='wide',
    initial_sidebar_state='auto')

DEPARTMENT_NAME = "Head Office"

st.markdown("# Head Office")
st.sidebar.header("Head Office")

# The `on_change` callback is correctly defined without calling it
timeframe = st.sidebar.radio(
    label="Select timeframe:",
    options=["Month", "Quarter", "Year"],
    index=1,
    key="timeframe",
    horizontal=True,
)
period_str_list = query_unique_timeframes(timeframe)
start_str = st.sidebar.selectbox(label="Start", options=period_str_list, index=len(period_str_list)-5, key="start_str")
end_str = st.sidebar.selectbox(label="End", options=period_str_list, index=len(period_str_list)-1, key="end_str")
if start_str > end_str:
    st.toast("Wrong period selected!", icon="🚨")
if "2020" in start_str or "2020" in end_str or "2021" in start_str or "2021" in end_str:
    st.toast("2020 and 2021 data cannot be splited by cost center!", icon="ℹ️")
if format_date_by_timeframe(timeframe) <= end_str:
    st.toast("You have selected the current period, data might be incomplete.", icon="ℹ️")

report_type = st.sidebar.radio(
    label="Select report type:",
    options=["Standard", "Adjusted_coef"],
    index=0,
    key="report_type",
    help=(
        "Staff*coef report adjustments:\n"
        "- Exclude Metos installment\n"
        "- Exclude holiday-, pension-, health insurance- related staff cost\n"
        "- Rest of the staff cost multiply by a factor according to country: (FI:1,37; EE:1,35; NO:1,30)\n"
    )
)
custom_adjustment = st.sidebar.toggle(
    "Custom adjustment",
    value=True,
    key="custom_adjustment",
    help=(
        "Making the following adjustments for easier interpretation:\n"
        "- Norwegian krone exchange rate: 10 NOK = 1 EUR\n"
        "- Internal company admin transfer fee modification\n"
        "- Modify the unallocated records\n"
    ),
)


search_btn = st.sidebar.button("Search")

if search_btn:
    po_tab1, po_tab2 = st.tabs(["Figure", "Data"])
    df = query_performance_overview_data(department_name=DEPARTMENT_NAME, report_type=report_type, start_str=start_str, end_str=end_str, timeframe=timeframe, custom_adjustment=custom_adjustment)
    df = prepare_performance_overview_data(df)
    with po_tab1:
        st.plotly_chart(make_performance_overview_graph(df), use_container_width=True)
    with po_tab2:
        st.dataframe(df, use_container_width=True, hide_index=True)