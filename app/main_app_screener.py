import streamlit as st
import os

from src.fmp.fmp_config import FMP_DATA_DIR
from src.main import process_tickers
from src.config_screener import SCREENER_PARAMS
import src.global_variables as gv
from src.utils import (
    add_ticker_current_info,
    load_tickers_blacklist,
    save_tickers_blacklist,
)

st.set_page_config(
    page_title="Stock Screener",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            padding-left: 4rem;
            padding-right: 4rem;
            max-width: 1400px;
        }

        /* Titles and Headers */
        h1 {
            color: #FFFFFF;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 2rem !important;
        }

        .section-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #10B981; /* Emerald Green */
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0F172A; /* Deep Slate */
            border-right: 1px solid #1E293B;
        }
        
        [data-testid="stSidebar"] .stMarkdown p {
            font-weight: 600;
        }

        /* Card-like Look for Sections */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre;
            background-color: transparent;
            border-radius: 4px 4px 0px 0px;
            color: #94A3B8;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            color: #10B981 !important;
            border-bottom-color: #10B981 !important;
        }

        /* Input Styling */
        .stNumberInput input, .stTextInput input, .stMultiSelect [data-baseweb="select"] {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            color: #F8FAFC !important;
        }

        /* Button Styling */
        .stButton button {
            background-color: #1E293B;
            color: #F8FAFC;
            border: 1px solid #334155;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
            width: 100%;
        }

        .stButton button:hover {
            border-color: #10B981;
            color: #10B981;
            background-color: #0F172A;
        }

        /* Metrics/Info Box */
        .info-box {
            background-color: #1E293B;
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid #334155;
            margin-bottom: 1rem;
        }

        /* Dividers */
        hr {
            margin: 2rem 0;
            border-color: #334155;
            opacity: 0.3;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Magic Screener")
available_tickers = os.listdir(FMP_DATA_DIR)
available_tickers.sort()

# Load blacklist and identify whitelisted tickers at startup
blacklist_data = load_tickers_blacklist()
blacklisted_tickers = blacklist_data.get("tickers", [])
whitelisted_tickers = [t for t in available_tickers if t not in blacklisted_tickers]

with st.sidebar:
    st.markdown(
        '<div class="section-header">Screener Parameters</div>',
        unsafe_allow_html=True,
    )
    fcf_years = st.number_input(
        label="Years FCF growth:",
        min_value=1,
        max_value=4,
        value=3,
        step=1,
        help="Number of years to calculate Free Cash Flow (FCF) growth.",
        key="fcf_years_input",
    )
    ocf_years = st.number_input(
        label="Years OCF growth:",
        min_value=1,
        max_value=4,
        value=3,
        step=1,
        help="Number of years to calculate Operating Cash Flow (OCF) growth.",
        key="ocf_years_input",
    )
    st.write("---")

tab1, tab2 = st.tabs(["Screener", "Compare"])

with tab1:
    st.markdown(
        '<div class="section-header">Select Stocks</div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([0.6, 0.4], gap="medium")

    with col_left:
        col_score, col_toggle = st.columns([1, 2])
        with col_score:
            min_score = st.number_input(
                label="Min Score:",
                min_value=0,
                value=0,
                step=1,
                help="Minimum score to filter stocks.",
                key="min_score_input",
            )
        with col_toggle:
            st.write("")  # Vertical spacer to align with number inputs
            st.write("")
            current_data_dl = st.toggle(
                label="download current data", key="current_data_dl_toggle"
            )

        # Create an object (dictionary) to pass parameters
        screener_parameters = {
            gv.FCF_YEARS: fcf_years,
            gv.OCF_YEARS: ocf_years,
        }

        col_multiselect, col_select_all, col_select_whitelisted = st.columns([3, 1, 1])
        with col_multiselect:
            selected_tickers = st.multiselect(
                label="Select stock tickers:",
                options=available_tickers,
                placeholder="Type or select tickers...",
                help="Start typing to filter the list of available stock tickers.",
                label_visibility="collapsed",
            )

        with col_select_all:
            if st.button("Select All"):
                selected_tickers = available_tickers

        with col_select_whitelisted:
            if st.button("Select Whitelisted"):
                selected_tickers = whitelisted_tickers

    # --- Blacklist Section in Sidebar ---
    with st.sidebar:
        if blacklist_data:
            st.markdown(
                '<div class="section-header"> Tickers Blacklist</div>',
                unsafe_allow_html=True,
            )
            with st.container():
                st.markdown(
                    f"""
                    <div class="info-box">
                        <div style="font-size: 0.85rem; color: #94A3B8;">Date</div>
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">{blacklist_data.get('date', 'N/A')}</div>
                        <div style="font-size: 0.85rem; color: #94A3B8;">Threshold</div>
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">{blacklist_data.get('threshold_score', 'N/A')}</div>
                        <div style="font-size: 0.85rem; color: #94A3B8;">Tickers</div>
                        <div style="font-weight: 600;">{len(blacklisted_tickers)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            bl_threshold = st.number_input(
                "BL Threshold:",
                min_value=0,
                value=int(blacklist_data.get("threshold_score", 0)),
                key="bl_threshold_input",
            )
            if st.button("Update Blacklist"):
                with st.spinner("Updating Blacklist..."):
                    df_scores_bl, df_features_bl = process_tickers(
                        available_tickers, screener_parameters
                    )
                    save_tickers_blacklist(df_scores_bl, bl_threshold)
                    # Reload blacklist data to update UI info
                    blacklist_data = load_tickers_blacklist()
                    blacklisted_tickers = blacklist_data.get("tickers", [])
                    st.info(
                        f"Blacklist updated! {len(blacklisted_tickers)} tickers placed in the new blacklist."
                    )
    # ------------------------------------

    df_scores, df_features = process_tickers(selected_tickers, screener_parameters)

    # Filter by score
    if not df_scores.empty:
        df_scores = df_scores[df_scores[gv.SCORE] >= min_score]

    with col_right:
        if not df_scores.empty:
            st.markdown(
                '<div class="section-header">Score Distribution</div>',
                unsafe_allow_html=True,
            )
            score_counts = df_scores[gv.SCORE].value_counts().reset_index()
            score_counts.columns = [gv.SCORE, "Occurrences"]
            score_counts = score_counts.sort_values(by=gv.SCORE)

            st.bar_chart(score_counts, x=gv.SCORE, y="Occurrences", height=200)
        else:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.info("Select tickers to see score distribution.")

    st.write("---")

    if not df_scores.empty:
        st.markdown(
            '<div class="section-header"> Screener Results</div>',
            unsafe_allow_html=True,
        )
        print("checking if current data should be added")
        if current_data_dl:
            print("Adding current data to screener results")
            progress_bar = st.progress(0, text="Fetching current data...")

            def update_progress(progress):
                progress_bar.progress(
                    progress, text=f"Fetching current data... {int(progress * 100)}%"
                )

            df_scores = add_ticker_current_info(
                df_scores, progress_callback=update_progress
            )
            progress_bar.empty()
        st.dataframe(df_scores, width="stretch")
    else:
        st.info(
            "No data to display for Screener Results (Scores). Please select and process tickers."
        )

    st.write("---")
    if not df_features.empty:
        st.markdown(
            '<div class="section-header"><span>🔍</span> Detailed Features Data</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(df_features, width="stretch")
    else:
        st.info(
            "No data to display for Detailed Features Data. Please select and process tickers."
        )
