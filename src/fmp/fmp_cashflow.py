import os
import pandas as pd
from typing import List

from src.fmp.fmp_config import FMP_DATA_DIR
from src.fmp.fmp_global_variables import GlobalVars as fmp_gv
import src.global_variables as gv


class FmpDataCashFlow:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.json_file_cashflow = os.path.join(
            FMP_DATA_DIR, self.ticker, f"{self.ticker}_cash-flow-statement.json"
        )
        self.df_cashflow = self._get_cashflow_data()

    def _get_cashflow_data(self) -> pd.DataFrame | None:
        """
        Loads cash flow statement data from a JSON file for the given ticker.

        The data is expected to be in descending order by date and is
        then reversed to be in ascending order (oldest to newest) and
        the index is reset.

        Returns:
            pd.DataFrame | None: A DataFrame containing the cash flow data,
                                 or None if the file does not exist or is empty.
        """
        if os.path.exists(self.json_file_cashflow):
            self.df_cashflow = pd.read_json(self.json_file_cashflow)
            if self.df_cashflow.empty:
                print(f"Warning: Cash flow data for {self.ticker} is empty.")
                return None
            # reverse order of rows to be chronological (oldest to newest), reset index
            self.df_cashflow = self.df_cashflow.iloc[::-1].reset_index(drop=True)
            return self.df_cashflow
        else:
            print(f"Error: data for ticker {self.ticker} not found. Implement fmp API")
            return None

    def is_free_cashflow_increasing(self, n: int = 2) -> (bool, dict):
        """
        Checks if the cash flow values for the most recent `n` years are continually increasing,
        and if the most recent cash flow value is positive.
        """
        fcf_labels = [
            fmp_gv.fcf_4_year_ago,
            fmp_gv.fcf_3_year_ago,
            fmp_gv.fcf_2_year_ago,
            fmp_gv.fcf_1_year_ago,
        ]
        if self.df_cashflow is None or self.df_cashflow.empty:
            return False
        n = min(n, 4)
        if n < 2:
            return False
        if len(self.df_cashflow) < n:
            return False

        recent_cashflow_values = self.df_cashflow[fmp_gv.freeCashFlow].iloc[-n:]

        selected_labels = fcf_labels[-n:]
        cashflow_dict = dict(zip(selected_labels, recent_cashflow_values.tolist()))

        is_continually_increasing = True
        for i in range(n - 1):
            if recent_cashflow_values.iloc[i] >= recent_cashflow_values.iloc[i + 1]:
                is_continually_increasing = False
                break

        is_last_value_positive = recent_cashflow_values.iloc[-1] > 0
        cashflow_trend_criterium = is_continually_increasing and is_last_value_positive

        return cashflow_trend_criterium, cashflow_dict

    def is_operative_cashflow_increasing(self, n: int = 2) -> (bool, dict):
        """
        Checks if the cash flow values for the most recent `n` years are continually increasing,
        and if the most recent cash flow value is positive.
        """
        ocf_labels = [
            fmp_gv.ocf_4_year_ago,
            fmp_gv.ocf_3_year_ago,
            fmp_gv.ocf_2_year_ago,
            fmp_gv.ocf_1_year_ago,
        ]
        if self.df_cashflow is None or self.df_cashflow.empty:
            return False
        n = min(n, 4)
        if n < 2:
            return False
        if len(self.df_cashflow) < n:
            return False

        recent_cashflow_values = self.df_cashflow[fmp_gv.operative_cash_flow].iloc[-n:]

        selected_labels = ocf_labels[-n:]
        cashflow_dict = dict(zip(selected_labels, recent_cashflow_values.tolist()))

        is_continually_increasing = True
        for i in range(n - 1):
            if recent_cashflow_values.iloc[i] >= recent_cashflow_values.iloc[i + 1]:
                is_continually_increasing = False
                break

        is_last_value_positive = recent_cashflow_values.iloc[-1] > 0
        cashflow_trend_criterium = is_continually_increasing and is_last_value_positive

        return cashflow_trend_criterium, cashflow_dict

    @classmethod
    def collect_scores_and_features(
        cls, tickers_list: List[str], screener_params: dict
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Collects Free Cash Flow (FCF) and Operative Cash Flow (OCF) features and scores
        indicating if they are increasing for a list of tickers.
        Args:
            tickers_list (List[str): A list of ticker symbols to process.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two DataFrames:
                - df_scores: Contains boolean scores indicating if FCF and OCF are continually
                  increasing and positive for each ticker.
                - df_features: Contains FCF and OCF data for the past 'n' years for each ticker.
                :param screener_params: dictionary with screener params
        """
        all_ticker_features = []
        all_ticker_scores = []
        for t in tickers_list:
            try:
                cashflow = cls(ticker=t)
                # Retrieve FCF data and score
                years_fcf = screener_params.get(gv.FCF_YEARS, 3)
                is_fcf_increasing, fcf_data = cashflow.is_free_cashflow_increasing(
                    n=years_fcf
                )
                # Retrieve OCF data and score
                years_ocf = screener_params.get(gv.OCF_YEARS, 3)
                is_ocf_increasing, ocf_data = cashflow.is_operative_cashflow_increasing(
                    n=years_ocf
                )

                row_data_features = {"ticker": t}
                row_data_features.update(fcf_data)
                row_data_features.update(ocf_data)
                all_ticker_features.append(row_data_features)

                row_data_scores = {
                    "ticker": t,
                    fmp_gv.increasing_fcf_condition: is_fcf_increasing,
                    fmp_gv.increasing_ocf_condition: is_ocf_increasing,  # Add OCF score
                }
                all_ticker_scores.append(row_data_scores)

            except Exception as e:
                print(f"Error processing ticker {t}: {e}")

        if all_ticker_features:
            df_features = pd.DataFrame(all_ticker_features)
        else:
            print("No valid feature data collected for any ticker.")
            df_features = pd.DataFrame()

        if all_ticker_scores:
            df_scores = pd.DataFrame(all_ticker_scores)
        else:
            print("No valid score data collected for any ticker.")
            df_scores = pd.DataFrame()

        return df_scores, df_features


if __name__ == "__main__":
    cashflow = FmpDataCashFlow("TEST")
    increasing_fcf = cashflow.is_free_cashflow_increasing(n=2)
    print(increasing_fcf)
    increasing_ocf = cashflow.is_operative_cashflow_increasing(n=3)
    print(increasing_ocf)
