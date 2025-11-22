import pandas as pd

from src.fmp.fmp_cashflow import FmpDataCashFlow
from src.utils import reorder_dataframes_columns, add_ticker_info, calculate_score


def process_tickers(tickers):

    if not tickers:
        return pd.DataFrame(), pd.DataFrame()

    # process Cash Flow Data
    df_scores, df_features = FmpDataCashFlow.collect_scores_and_features(tickers_list=tickers)
    df_scores = calculate_score(df_scores)
    df_scores, df_features, df_info_stocks = add_ticker_info(df_scores, df_features)
    df_scores, df_features = reorder_dataframes_columns(df_scores, df_features, df_info_stocks)

    return df_scores, df_features


if __name__ == "__main__":

    test_tickers = ["AACG", "TEST"]
    df_scores_test, df_features_test = process_tickers(test_tickers)

    print(df_features_test)
    print(df_scores_test)




