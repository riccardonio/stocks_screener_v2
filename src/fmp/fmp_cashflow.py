import os
import pandas as pd

from src.fmp.fmp_config import FMP_DATA_DIR
from src.fmp.fmp_global_variables import GlobalVars as gv


class FmpDataCashFlow:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.json_file_cashflow = os.path.join(
            FMP_DATA_DIR, self.ticker, f"{self.ticker}_cash-flow-statement.json"
        )
        self.df_cashflow = self._get_cashflow_data()

    def _get_cashflow_data(self):
        if os.path.exists(self.json_file_cashflow):
            # the rows are ordered in descending order of
            self.df_cashflow = pd.read_json(self.json_file_cashflow)
            if self.df_cashflow.empty:
                print(f"Warning: Cash flow data for {self.ticker} is empty.")
                return None
            # reverse order of rows, reset index
            self.df_cashflow = self.df_cashflow.iloc[::-1].reset_index()
            return self.df_cashflow
        else:
            print(f"Error: data for ticker {self.ticker} not found. Implement fmp API")
            return None

    def is_cashflow_increasing(self, n: int = 2) -> (bool, dict):
        """
        Checks if the cash flow values for the most recent `n` years are continually increasing,
        and if the most recent cash flow value is positive.
        """
        fcf_labels = [
            gv.fcf_4_year_ago,
            gv.fcf_3_year_ago,
            gv.fcf_2_year_ago,
            gv.fcf_1_year_ago,
        ]
        if self.df_cashflow is None or self.df_cashflow.empty:
            return False
        n = min(n, 4)
        if n < 2:
            return False
        if len(self.df_cashflow) < n:
            return False

        recent_cashflow_values = self.df_cashflow[gv.freeCashFlow].iloc[-n:]

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


if __name__ == "__main__":
    cashflow = FmpDataCashFlow("TEST")
    increasing_cf = cashflow.is_cashflow_increasing(n=2)
    print(increasing_cf)
