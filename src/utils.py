import pandas as pd

from src.finviz.finviz_screener import get_df_with_all_tickers_information
import src.global_variables as gv
from src.yfinance.yfinance_utils import YahooFinanceTickerInfo

def reorder_dataframes_columns(df_scores: pd.DataFrame,
                               df_features: pd.DataFrame,
                               df_info_stocks: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reorders the columns of df_scores and df_features according to specific rules:
    - Drops the 'Ticker' column (which originates from df_info_stocks after merge).
    - Places the columns originating from df_info_stocks (excluding the dropped 'Ticker')
      just after the 'ticker' column in both dataframes.

    Args:
        df_scores (pd.DataFrame): DataFrame containing scores and merged info.
        df_features (pd.DataFrame): DataFrame containing features and merged info.
        df_info_stocks (pd.DataFrame): Original DataFrame from get_df_with_all_tickers_information,
                                       used to identify which columns came from it.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: The modified df_scores and df_features with reordered columns.
    """

    info_cols_to_move = [col for col in df_info_stocks.columns if col != 'Ticker']

    def _reorder_df(df: pd.DataFrame, ticker_col_name: str = 'ticker') -> pd.DataFrame:
        if 'Ticker' in df.columns:
            df = df.drop(columns=['Ticker'])
        current_cols = df.columns.tolist()
        if ticker_col_name not in current_cols:
            return df

        info_cols_present_in_df = [col for col in info_cols_to_move if col in df.columns]

        other_cols = [col for col in current_cols
                      if col != ticker_col_name and col not in info_cols_present_in_df]

        new_order = [ticker_col_name] + info_cols_present_in_df + other_cols

        return df[new_order]

    df_scores = _reorder_df(df_scores)
    df_features = _reorder_df(df_features)

    return df_scores, df_features


def add_ticker_info(df_scores, df_features):

    df_info_stocks = get_df_with_all_tickers_information()
    df_scores = pd.merge(df_scores, df_info_stocks, left_on='ticker', right_on='Ticker', how='left')
    df_features = pd.merge(df_features, df_info_stocks, left_on='ticker', right_on='Ticker', how='left')
    return df_scores, df_features, df_info_stocks


def calculate_score(df_scores: pd.DataFrame) -> pd.DataFrame:
    score_columns = df_scores.select_dtypes(include='bool').columns
    df_scores[gv.SCORE] = df_scores[score_columns].sum(axis=1)

    # Reorder columns: 'score' should come before boolean columns
    non_score_and_bool_cols = [col for col in df_scores.columns if col not in score_columns and col != 'score']
    new_order = non_score_and_bool_cols + [gv.SCORE] + score_columns.tolist()
    df_scores = df_scores[new_order]

    return df_scores


def add_ticker_current_info(df_scores: pd.DataFrame) -> pd.DataFrame:
    """
    Adds multiple metrics (P/E, Insider Ownership, FCF, etc.) to the DataFrame
    by fetching data for each ticker efficiently.
    """
    # 1. Create the Analyzer object for each row
    # This triggers the API call ONCE per ticker
    stock_objects = df_scores['ticker'].apply(YahooFinanceTickerInfo)

    # 2. Extract all metrics at once into a new DataFrame
    # apply(pd.Series) expands the dictionary returned by get_all_metrics into columns
    metrics_df = stock_objects.apply(lambda x: pd.Series(x.get_all_metrics()))

    # 3. Concatenate the new metrics columns with the original DataFrame
    # axis=1 adds columns side-by-side
    df_scores = pd.concat([df_scores, metrics_df], axis=1)

    return df_scores

