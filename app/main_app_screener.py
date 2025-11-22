import streamlit as st
import os
import pandas as pd

from src.fmp.fmp_config import FMP_DATA_DIR
#from src.fmp.fmp_global_vars import GlobalVars as gv
from src.main import process_tickers
from src.config_screener import BLACK_LIST, SCREENER_PARAMS

st.set_page_config(
    page_title="Stock Screener",
    layout="wide",  # Can be "wide" or "centered"
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
)

st.title("Magic Screener")
available_tickers = os.listdir(FMP_DATA_DIR)
available_tickers = [
    ticker for ticker in available_tickers if ticker not in BLACK_LIST
]
available_tickers.sort()

tab1, tab2 = st.tabs(["Screener", "Compare"])

with tab1:
    selected_tickers = st.multiselect(
        label="Select stock tickers:",
        options=available_tickers,
        placeholder="Type or select tickers...",
        help="Start typing to filter the list of available stock tickers.",
    )
    col1, _ = st.columns([1, 2])
    with col1:
        with st.expander("View Screener Parameters"):
            params_df = pd.DataFrame(SCREENER_PARAMS.items(), columns=["Parameter", "Value"])
            st.dataframe(params_df, width='stretch', hide_index=True)

    st.markdown(
        f"<p style='font-size: 18px; color: #2ECC71;'>Available stocks: {len(available_tickers)}</p>",
        unsafe_allow_html=True,
    )

    if st.button("Select All"):
        selected_tickers = available_tickers

    st.write("---")

    df_scores, df_features = process_tickers(selected_tickers)
    if not df_scores.empty:
        st.dataframe(df_scores)
    else:
        st.info(
            "No data to display for Screener Results (Scores). Please select and process tickers."
        )
    st.write("---")
    if not df_features.empty:
        st.dataframe(df_features)
