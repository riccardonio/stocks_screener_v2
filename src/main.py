import pandas as pd

from src.fmp.fmp_cashflow import FmpDataCashFlow
from src.fmp.fmp_global_variables import GlobalVars as gv
from src.finviz.finviz_screener import get_df_with_all_tickers_information


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


if __name__ == "__main__":

    sample_tickers = ["AACG", "TEST", "MSFT"]
    df_scores, df_features = FmpDataCashFlow.collect_scores_and_features(tickers_list=sample_tickers)
    df_info_stocks = get_df_with_all_tickers_information()

    df_scores = pd.merge(df_scores, df_info_stocks, left_on='ticker', right_on='Ticker', how='left')
    df_features = pd.merge(df_features, df_info_stocks, left_on='ticker', right_on='Ticker', how='left')

    df_scores, df_features = reorder_dataframes_columns(df_scores, df_features, df_info_stocks)

    print(df_features)
    print(df_scores)




