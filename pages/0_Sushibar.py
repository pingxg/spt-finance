from PIL import Image
import streamlit as st
from analytics.query import *
from visuals.graphs import *


st.set_page_config(
    page_title="Sushibar",
    page_icon=Image.open("assets/logo.ico"),
    layout='wide',
    initial_sidebar_state='auto',
)

st.markdown("# Sushibar Project")
st.divider()

st.sidebar.header("Sushibar Project")


# The `on_change` callback is correctly defined without calling it
timeframe = st.sidebar.radio(
    label="Select timeframe:",
    options=["Month", "Quarter", "Year"],
    index=1,
    key="timeframe",
    horizontal=True,
)
period_str_list = query_unique_timeframes(timeframe)
start_str = st.sidebar.selectbox(label="Start", options=period_str_list, index=len(period_str_list)-3, key="start_str")
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
        "- Outsourced sushibar's other external services changed to staff cost"
        "- The restaurant rental income is offset by the rent expense\n"
        "- The restaurant section only records sales of directly operated stores and franchise fees\n"
        "- Gas expenses and business trip allowances in the restaurant are counted as part of the salary\n"
        "- Factory hot meal modification, costs are charged to the sushibar, sales are added to the factory\n"
        "- Factory's S-card purchase correction to fuel expenses\n"
        "- Factory's other external services changed to staff cost\n"
        "- Internal company admin transfer fee modification\n"
        "- Modify the unallocated records\n"
    ),
)

st.sidebar.toggle(
    "Split office cost",
    value=False,
    key="split_office_cost",
    help=(
        "Making the adjustments according to following rules:\n"
        "- Calcualte the sales (after the custom adjustments if set to true) for each cost center for every period\n"
        "- Split the cost for all the financial accounts that is booked as head office based on projects sales percentage\n"
        "- Note: the project's head offices are project-specific, for example head office sushibar belongs to sushibar project, not head office\n"
    )
)

search_btn = st.sidebar.button("Search")

if search_btn:
    po_tab1, po_tab2 = st.tabs(["Figure", "Data"])
    df = prepare_performance_overview_data(department_name="food kiosk sushibar", start_str=start_str, end_str=end_str, report_type=report_type)
    with po_tab1:
        st.plotly_chart(make_performance_overview_graph(df), use_container_width=True)
    with po_tab2:
        st.dataframe(df, use_container_width=True, hide_index=True)
