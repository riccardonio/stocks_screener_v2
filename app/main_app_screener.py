import streamlit as st
import os

from src.fmp.fmp_config import FMP_DATA_DIR
from src.main import process_tickers
from src.config_screener import BLACK_LIST, SCREENER_PARAMS
import src.global_variables as gv
from src.utils import add_ticker_current_info

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
    col_inputs, col_chart = st.columns([0.6, 0.4], gap="medium")

    with col_inputs:
        st.markdown(
            "<p style='font-size: 18px; color: #2ECC71; '>Screener Parameters</p>",
            unsafe_allow_html=True
        )

        col_fcf, col_ocf, col_dl = st.columns(3)
        with col_fcf:
            fcf_years = st.number_input(
                label="Years FCF growth:",
                min_value=1,
                max_value=4,
                value=3,
                step=1,
                help="Number of years to calculate Free Cash Flow (FCF) growth.",
                key="fcf_years_input"
            )
        with col_ocf:
            ocf_years = st.number_input(
                label="Years OCF growth:",
                min_value=1,
                max_value=4,
                value=3,
                step=1,
                help="Number of years to calculate Operating Cash Flow (OCF) growth.",
                key="ocf_years_input"
            )
        with col_dl:
            sub_col_score, sub_col_toggle = st.columns([1, 2])
            with sub_col_score:
                min_score = st.number_input(
                    label="Min Score:",
                    min_value=0,
                    value=0,
                    step=1,
                    help="Minimum score to filter stocks.",
                    key="min_score_input"
                )
            with sub_col_toggle:
                st.write("")  # Vertical spacer to align with number inputs
                st.write("")
                current_data_dl = st.toggle(
                    label="download current data",
                    key="current_data_dl_toggle"
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

        col_multiselect, col_select_all = st.columns([3, 1])
        with col_multiselect:
            selected_tickers = st.multiselect(
                label="Select stock tickers:",
                options=available_tickers,
                placeholder="Type or select tickers...",
                help="Start typing to filter the list of available stock tickers.",
                label_visibility="collapsed"
            )

        with col_select_all:
            if st.button("Select All"):
                selected_tickers = available_tickers

        # --- Blacklist Section ---
        from src.utils import load_tickers_blacklist
        blacklist_data = load_tickers_blacklist()
        if blacklist_data:
            st.write("---")
            st.markdown(
                "<p style='font-size: 18px; color: #E74C3C; '>Tickers Blacklist</p>",
                unsafe_allow_html=True
            )
            col_bl_info, col_bl_tickers = st.columns([1, 2])
            with col_bl_info:
                st.write(f"**Date:** {blacklist_data.get('date', 'N/A')}")
                st.write(f"**Threshold:** {blacklist_data.get('threshold_score', 'N/A')}")
            with col_bl_tickers:
                st.write(f"**Tickers:** {', '.join(blacklist_data.get('tickers', []))}")
        # -------------------------

    df_scores, df_features = process_tickers(selected_tickers, screener_parameters)

    # Filter by score
    if not df_scores.empty:
        df_scores = df_scores[df_scores[gv.SCORE] >= min_score]

    with col_chart:
        if not df_scores.empty:
            st.markdown(
                f"<p style='font-size: 18px; color: #2ECC71;'>Score Distribution</p>",
                unsafe_allow_html=True,
            )
            score_counts = df_scores[gv.SCORE].value_counts().reset_index()
            score_counts.columns = [gv.SCORE, 'Occurrences']
            score_counts = score_counts.sort_values(by=gv.SCORE)

            st.bar_chart(score_counts, x=gv.SCORE, y='Occurrences', height=300)
        else:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.info("Select tickers to see score distribution.")


    st.write("---")

    if not df_scores.empty:
        st.markdown(
            f"<p style='font-size: 18px; color: #2ECC71;'>Screener Results</p>",
            unsafe_allow_html=True,
        )
        print("checking if current data should be added")
        if current_data_dl:
            print("Adding current data to screener results")
            progress_bar = st.progress(0, text="Fetching current data...")
            
            def update_progress(progress):
                progress_bar.progress(progress, text=f"Fetching current data... {int(progress * 100)}%")
                
            df_scores = add_ticker_current_info(df_scores, progress_callback=update_progress)
            progress_bar.empty()
        st.dataframe(df_scores, width='stretch')
    else:
        st.info(
            "No data to display for Screener Results (Scores). Please select and process tickers."
        )

    st.write("---")
    if not df_features.empty:
        st.subheader("Detailed Features Data")
        st.dataframe(df_features, width='stretch')
    else:
        st.info(
            "No data to display for Detailed Features Data. Please select and process tickers."
        )