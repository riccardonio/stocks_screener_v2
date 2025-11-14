import pandas as pd

from src.fmp.fmp_cashflow import FmpDataCashFlow
from src.fmp.fmp_global_variables import GlobalVars as gv




if __name__ == "__main__":
    # Example usage:
    # Replace with your desired list of tickers
    sample_tickers = ["AACG", "TEST", "MSFT"]
    df_scores, df_features = FmpDataCashFlow.collect_scores_and_features(tickers_list=sample_tickers)
    print(df_features)
    print(df_scores)




