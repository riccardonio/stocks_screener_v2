from finvizfinance.screener.overview import Overview
import pandas as pd

from src.global_variables import ALL_STOCKS_INFO_FILE


def get_all_ticker_from_finviz():
    try:
        foverview = Overview()
        ticker_list = foverview.screener_view(order="Ticker")
        desired_columns = ["Ticker", "Company", "Sector", "Industry", "Country"]
        ticker_list = ticker_list[desired_columns]

        ticker_list.to_csv(ALL_STOCKS_INFO_FILE, index=False)
        print(f"Found {len(ticker_list)} tickers (sample): {ticker_list.head(10)}")

    except Exception as e:
        print(f"Error using finvizfinance: {e}")
        print(
            "Note: finvizfinance relies on scraping and might require updates if Finviz changes."
        )


def get_df_with_all_tickers_information():
    return pd.read_csv(ALL_STOCKS_INFO_FILE)


if __name__ == "__main__":
    # get_all_ticker_from_finviz()
    df = get_df_with_all_tickers_information()
    print("OK")
