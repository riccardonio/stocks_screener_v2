import pandas as pd
import numerize.numerize as nm

from src.fmp.fmp_cashflow import FmpDataCashFlow
from src.utils import reorder_dataframes_columns, add_ticker_info, calculate_score
# TODO: pass the screener_parameters to the functions to calculate scores
def process_tickers(
    tickers: list[str],
    screener_parameters: dict
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Processes financial data for a list of stock tickers, calculates scores,
    adds additional information, and returns two sorted pandas DataFrames.

    Args:
        tickers (list[str]): A list of stock ticker symbols to process.
        screener_parameters (dict): A dictionary containing parameters for the screener,
                                    e.g., fcf_years, ocf_years.
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two pandas DataFrames:
            - df_scores (pd.DataFrame): DataFrame with calculated scores and ticker information,
              sorted by score in descending order.
            - df_features (pd.DataFrame): DataFrame with collected features, calculated scores,
              and ticker information, sorted by score in descending order.
    """
    if not tickers:
        return pd.DataFrame(), pd.DataFrame()

    # process Cash Flow Data
    df_scores, df_features = FmpDataCashFlow.collect_scores_and_features(tickers_list=tickers,
                                                                         screener_params=screener_parameters)
    # add scores to both dfs
    df_scores = calculate_score(df_scores)
    df_features['score'] = df_scores['score']
    # add more info
    df_scores, df_features, df_info_stocks = add_ticker_info(df_scores, df_features)
    # reorder
    df_scores, df_features = reorder_dataframes_columns(df_scores, df_features, df_info_stocks)
    # reorder both output dfs by "score" in descending order
    df_scores = df_scores.sort_values(by="score", ascending=False)
    df_features = df_features.sort_values(by="score", ascending=False)

    # Apply numerize.numerize to all numerical values in df_features
    numerical_cols = df_features.select_dtypes(include=['number']).columns
    for col in numerical_cols:
        if col not in ['score']: # Add other columns to exclude if necessary, e.g., 'sharesOuts' if it's already an int
            df_features[col] = df_features[col].apply(lambda x: nm.numerize(x) if pd.notnull(x) else x)

    return df_scores, df_features


if __name__ == "__main__":
    SCREENER_PARAMS = {
        "fcf_years" : 3,
        "ocf_years" : 2
    }
    test_tickers = ["AACG", "TEST", "AAL"]
    df_scores_test, df_features_test = process_tickers(test_tickers,
                                                       screener_parameters=SCREENER_PARAMS)

    print(df_features_test)
    print(df_scores_test)




