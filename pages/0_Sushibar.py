import logging
from PIL import Image
import streamlit as st
from analytics.query import *
from visuals.graphs import *

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEPARTMENT_NAME = 'Food Kiosk Sushibar'
PAGE_TITLE = "Sushibar"
PAGE_ICON = "assets/logo.ico"
TIMEFRAME_OPTIONS = ["Month", "Quarter", "Year"]
REPORT_TYPE_OPTIONS = ["Standard", "Adjusted_coef"]
TURNOVER_FILTER_OPTIONS = ["Manager", "Product category", "Location name", "City", "Country", "Status"]

# Page Configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=Image.open(PAGE_ICON),
    layout='wide',
    initial_sidebar_state='auto',
)

# Page Header
st.markdown(f"# {PAGE_TITLE} Project")
st.sidebar.header(f"{PAGE_TITLE} Project")

# Initialize session state
if 'pivot_by' not in st.session_state:
    st.session_state['pivot_by'] = "Manager"
    logger.info("Initialized session state with default pivot_by value: Manager")

# Sidebar Widgets
def create_sidebar_widgets():
    logger.info("Creating sidebar widgets")
    timeframe = st.sidebar.radio(
        label="Select timeframe:",
        options=TIMEFRAME_OPTIONS,
        index=1,
        key="timeframe",
        horizontal=True,
    )
    period_str_list = query_unique_timeframes(timeframe)
    start_str = st.sidebar.selectbox(label="Start", options=period_str_list, index=len(period_str_list)-5, key="start_str")
    end_str = st.sidebar.selectbox(label="End", options=period_str_list, index=len(period_str_list)-1, key="end_str")
    
    if start_str > end_str:
        st.toast("Wrong period selected!", icon="🚨")
        logger.warning(f"Invalid date range selected: {start_str} to {end_str}")
    if any(year in start_str or year in end_str for year in ["2020", "2021"]):
        st.toast("2020 and 2021 data cannot be splited by cost center!", icon="ℹ️")
        logger.info("User selected data from 2020 or 2021")
    if format_date_by_timeframe(timeframe) <= end_str:
        st.toast("You have selected the current period, data might be incomplete.", icon="ℹ️")
        logger.info("User selected current period, data may be incomplete")

    report_type = st.sidebar.radio(
        label="Select report type:",
        options=REPORT_TYPE_OPTIONS,
        index=0,
        key="report_type",
        help=(
            "Staff*coef report adjustments:\n"
            "- Exclude Metos installment\n"
            "- Exclude holiday-, pension-, health insurance- related staff cost\n"
            "- Rest of the staff cost multiply by a factor according to country: (FI:1,37; EE:1,35; NO:1,30)\n"
        )
    )

    selected_option = st.sidebar.radio(
        "Select turnover filter:", 
        options=TURNOVER_FILTER_OPTIONS, 
        key='pivot_by',
        index=TURNOVER_FILTER_OPTIONS.index(st.session_state['pivot_by']) if st.session_state['pivot_by'] in TURNOVER_FILTER_OPTIONS else 0,
        horizontal=True, 
        help="Note: Turnover figures may differ from the performance analysis because the performance analysis's amounts are calculated on a weekly basis, while turnover data is calculated monthly."
    )

    custom_adjustment = st.sidebar.toggle(
        "Custom adjustment",
        value=True,
        key="custom_adjustment",
        help=(
            "Making the following adjustments for easier interpretation:\n"
            "- Estonia cost adjustments (4385 > Finance; 4395 > Admin; 4300 > Marketing)\n"
            "- Norway cost adjustments (6700, 6705 > Finance; 6720, 6790 > Admin; 7320 > Marketing)\n"
            "- Norwegian krone exchange rate: 10 NOK = 1 EUR\n"
            "- Outsourced sushibar's other external services changed to staff cost\n"
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
            "- Calculate the sales (after the custom adjustments if set to true) for each cost center for every period\n"
            "- Split the cost for all the financial accounts that is booked as head office based on projects sales percentage\n"
            "- Note: the project's head offices are project-specific, for example head office sushibar belongs to sushibar project, not head office\n"
        )
    )

    logger.info(f"Sidebar widgets created with timeframe: {timeframe}, start: {start_str}, end: {end_str}, report_type: {report_type}")
    return timeframe, start_str, end_str, report_type, custom_adjustment, split_office_cost

# Main Function
def main():
    logger.info("Starting main function")
    timeframe, start_str, end_str, report_type, custom_adjustment, split_office_cost = create_sidebar_widgets()
    
    if st.sidebar.button("Search"):
        logger.info("Search button clicked")
        try:
            df = query_performance_overview_data(
                department_name=DEPARTMENT_NAME,
                report_type=report_type,
                start_str=start_str,
                end_str=end_str,
                timeframe=timeframe,
                custom_adjustment=custom_adjustment,
                split_office_cost=split_office_cost,
            )
            ss_df = query_sales_data(
                department_name=DEPARTMENT_NAME,
                start_str=start_str,
                end_str=end_str,
                timeframe=timeframe,
            )
            ss_avg_df = prepare_avg_sales_data(ss_df)

            display_performance_analysis(df)
            display_turnover_breakdown(ss_df, ss_avg_df)
            display_cost_structure(df)
            display_cost_details(df)
            logger.info("All data displayed successfully")
        except Exception as e:
            logger.error(f"Error occurred while processing data: {str(e)}")
            st.error("An error occurred while processing the data. Please try again.")

def display_performance_analysis(df):
    logger.info("Displaying performance analysis")
    st.subheader(f'Performance Analysis{" - " + DEPARTMENT_NAME if DEPARTMENT_NAME else ""}')
    po_fig_tab, po_data_tab = st.tabs(["Figure", "Data"])
    po_df = prepare_performance_overview_data(df, denominator="sales")
    with po_fig_tab:
        st.plotly_chart(make_performance_overview_graph(po_df), use_container_width=True)
    with po_data_tab:
        st.dataframe(po_df, use_container_width=True, hide_index=True)

def display_turnover_breakdown(ss_df, ss_avg_df):
    logger.info("Displaying turnover breakdown")
    st.subheader(f'Turnover Breakdown{" - " + DEPARTMENT_NAME if DEPARTMENT_NAME else ""}')
    ts_fig1_tab, ts_fig2_tab, ts_data_tab = st.tabs(["Turnover", "Average sales", "Data"])
    ts_df = prepare_turnover_structure_data(df=ss_df, department_name=DEPARTMENT_NAME, pivot_by=st.session_state['pivot_by'].lower().replace(" ", "_"))
    with ts_fig1_tab:
        st.plotly_chart(make_turnover_structure_graph(ts_df, department_name=DEPARTMENT_NAME), use_container_width=True)
    with ts_fig2_tab:
        st.plotly_chart(make_avg_sales_graph(ss_avg_df), use_container_width=True)
    with ts_data_tab:
        st.dataframe(ts_df, use_container_width=True, hide_index=True)

def display_cost_structure(df):
    logger.info("Displaying cost structure")
    st.subheader(f'Cost Structure{" - " + DEPARTMENT_NAME if DEPARTMENT_NAME else ""}')
    cs_fig1_tab, cs_fig2_tab, cs_data_tab = st.tabs(["Cost to Sales Ratio", "Cost to Total Cost Ratio", "Data"])
    with cs_fig1_tab:
        cs_df = prepare_performance_overview_data(df, denominator="sales")
        st.plotly_chart(make_cost_structure_graph(cs_df, denominator="sales"), use_container_width=True)
    with cs_fig2_tab:
        cs_df = prepare_performance_overview_data(df, denominator="costs")
        st.plotly_chart(make_cost_structure_graph(cs_df, denominator="costs"), use_container_width=True)
    with cs_data_tab:
        st.dataframe(cs_df, use_container_width=True, hide_index=True)

def display_cost_details(df):
    logger.info("Displaying cost details")
    st.subheader(f'Cost Details{" - " + DEPARTMENT_NAME if DEPARTMENT_NAME else ""}')
    cdd_fig_tab, cdd_data_tab = st.tabs(["Cumulative Cost Details Breakdown", "Data"])
    cdd_df = df.copy()
    with cdd_fig_tab:
        processed_df = prepare_cost_structure_cumulative_icicle(cdd_df)
        st.plotly_chart(make_cost_structure_cumulative_icicle_graph(processed_df), use_container_width=True)
    with cdd_data_tab:
        st.dataframe(cdd_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    logger.info("Starting Sushibar application")
    main()
    logger.info("Sushibar application finished")
