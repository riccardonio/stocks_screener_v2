import streamlit as st
import os


from src.fmp.fmp_config import FMP_DATA_DIR
from src.main import process_tickers
from src.config_screener import BLACK_LIST, SCREENER_PARAMS
import src.global_variables as gv

st.set_page_config(
    page_title="Stock Screener",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title("Magic Screener")
available_tickers = os.listdir(FMP_DATA_DIR)
available_tickers = [
    ticker for ticker in available_tickers if ticker not in BLACK_LIST
]
available_tickers.sort()

tab1, tab2 = st.tabs(["Screener", "Compare"])

with tab1:
    st.markdown(
        "<p style='font-size: 18px; color: #2ECC71; '>Screener Parameters</p>",
        unsafe_allow_html=True
    )
    col_fcf, col_ocf, _ = st.columns([0.1, 0.1, 0.8])
    with col_fcf:
        fcf_years = st.number_input(
            label="Years for FCF growth:",
            min_value=1,
            max_value=4,
            value=3,
            step=1,
            help="Number of years to calculate Free Cash Flow (FCF) growth.",
            key="fcf_years_input"
        )
    with col_ocf:
        ocf_years = st.number_input(
            label="Years for OCF growth:",
            min_value=1,
            max_value=4,
            value=3,
            step=1,
            help="Number of years to calculate Operating Cash Flow (OCF) growth.",
            key="ocf_years_input"
        )

    # Create an object (dictionary) to pass parameters
    screener_parameters = {
        gv.FCF_YEARS: fcf_years,
        gv.OCF_YEARS: ocf_years,
    }

    st.markdown(
        f"<p style='font-size: 18px; color: #2ECC71;'>Available stocks: {len(available_tickers)}</p>",
        unsafe_allow_html=True,
    )
    col_multiselect, col_select_all = st.columns([1, 3])
    with col_multiselect:
        selected_tickers = st.multiselect(
            label="Select stock tickers:",
            options=available_tickers,
            placeholder="Type or select tickers...",
            help="Start typing to filter the list of available stock tickers.",
        )

    with col_select_all:
        # Add a div with flex-grow to push the button to the bottom of its column
        st.markdown('<div style="flex-grow: 1;"></div>', unsafe_allow_html=True)
        if st.button("Select All"):
            selected_tickers = available_tickers

    st.write("---")

    df_scores, df_features = process_tickers(selected_tickers, screener_parameters)
    if not df_scores.empty:
        st.dataframe(df_scores)
    else:
        st.info(
            "No data to display for Screener Results (Scores). Please select and process tickers."
        )
    st.write("---")
    if not df_features.empty:
        st.dataframe(df_features)
