
from PIL import Image
import streamlit as st
from analytics.query import *
from visuals.graphs import *


st.set_page_config(
    page_title="Factory",
    page_icon=Image.open("assets/logo.ico"),
    layout='wide',
    initial_sidebar_state='auto')

DEPARTMENT_NAME = "Food Plant"

# # Initialize the session state variable for the radio selection if it doesn't exist
if 'pivot_by' not in st.session_state:
    st.session_state['pivot_by'] = "Location name"  # Set a default selection.

st.markdown("# Factory Project")
st.sidebar.header("Factory Project")

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


options = ["Location name", "Product category"]

selected_option = st.sidebar.radio(
    "Select turnover filter:", 
    options=options, 
    key='pivot_by',  # Use a consistent key for the widget.
    index=options.index(st.session_state['pivot_by']) if st.session_state['pivot_by'] in options else 0,  # Set the default selection based on the session state.
    horizontal=True, 
    help="Note: Turnover figures may differ from the performance analysis because the performance analysis's amounts are calculated on a weekly basis, while turnover data is calculated monthly."
)


custom_adjustment = st.sidebar.toggle(
    "Custom adjustment",
    value=True,
    key="custom_adjustment",
    help=(
        "Making the following adjustments for easier interpretation:\n"
        "- Factory hot meal modification, costs are charged to the sushibar, sales are added to the factory\n"
        "- Factory's S-card purchase correction to fuel expenses\n"
        "- Factory's other external services changed to staff cost\n"
        "- Mileage and daily allowances in the Factory are counted as part of the salary\n"
        "- Internal company admin transfer fee modification\n"
        "- Modify the unallocated records\n"
    ),
)

split_office_cost = st.sidebar.toggle(
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

# if search_btn:
#     po_tab1, po_tab2 = st.tabs(["Figure", "Data"])
#     df = query_performance_overview_data(department_name=DEPARTMENT_NAME, report_type=report_type, start_str=start_str, end_str=end_str, timeframe=timeframe, custom_adjustment=custom_adjustment)
#     df = prepare_performance_overview_data(df)
#     with po_tab1:
#         st.plotly_chart(make_performance_overview_graph(df), use_container_width=True)
#     with po_tab2:
#         st.dataframe(df, use_container_width=True, hide_index=True)


if search_btn:
    df = query_performance_overview_data(
        department_name=DEPARTMENT_NAME,
        report_type=report_type,
        start_str=start_str,
        end_str=end_str,
        timeframe=timeframe,
        custom_adjustment=custom_adjustment,
        split_office_cost=split_office_cost,
    )
    
    st.subheader(f'Performance Analysis{" - " + DEPARTMENT_NAME if DEPARTMENT_NAME is not None else ""}')
    po_fig_tab, po_data_tab = st.tabs(["Figure", "Data"])
    po_df = prepare_performance_overview_data(df, denominator="sales")
    with po_fig_tab:
        st.plotly_chart(make_performance_overview_graph(po_df), use_container_width=True)
    with po_data_tab:
        st.dataframe(po_df, use_container_width=True, hide_index=True)

    st.subheader(f'Turnover Breakdown{" - " + DEPARTMENT_NAME if DEPARTMENT_NAME is not None else ""}')
    ts_fig_tab, ts_data_tab = st.tabs(["Figure", "Data"])
    ts_df = prepare_turnover_structure_data(df, department_name=DEPARTMENT_NAME, pivot_by=st.session_state['pivot_by'].lower().replace(" ", "_"))
    with ts_fig_tab:
        st.plotly_chart(make_turnover_structure_graph(ts_df, department_name=DEPARTMENT_NAME), use_container_width=True)
    with ts_data_tab:
        st.dataframe(ts_df, use_container_width=True, hide_index=True)

    st.subheader(f'Cost Structure{" - " + DEPARTMENT_NAME if DEPARTMENT_NAME is not None else ""}')
    cs_fig1_tab, cs_fig2_tab, cs_data_tab = st.tabs(["Cost to Sales Ratio", "Cost to Total Cost Ratio", "Data"])
    
    with cs_fig1_tab:
        cs_df = prepare_performance_overview_data(df, denominator="sales")
        st.plotly_chart(make_cost_structure_graph(cs_df, denominator="sales"), use_container_width=True)
    with cs_fig2_tab:
        cs_df = prepare_performance_overview_data(df, denominator="costs")
        st.plotly_chart(make_cost_structure_graph(cs_df, denominator="costs"), use_container_width=True)
    with cs_data_tab:
        st.dataframe(cs_df, use_container_width=True, hide_index=True)

    st.subheader(f'Cost Details{" - " + DEPARTMENT_NAME if DEPARTMENT_NAME is not None else ""}')
    cdd_fig_tab, cdd_data_tab = st.tabs([ "Cumulative Cost Details Breakdown", "Data"])
    cdd_df = df.copy()
    with cdd_fig_tab:
        processed_df = prepare_cost_structure_cumulative_icicle(cdd_df)
        st.plotly_chart(make_cost_structure_cumulative_icicle_graph(processed_df), use_container_width=True)
    with cdd_data_tab:
        st.dataframe(cdd_df, use_container_width=True, hide_index=True)
