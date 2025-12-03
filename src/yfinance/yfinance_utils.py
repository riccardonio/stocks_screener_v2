import yfinance as yf

import src.yfinance.config_yahoo_finance as cyf
import src.global_variables as gv

class YahooFinanceTickerInfo:
    def __init__(self, ticker):
        self.ticker = ticker
        self.info = {}
        self._fetch_data()

    def _fetch_data(self):
        """
        Fetches data from yfinance once and stores it in self.info.
        """
        try:
            tkr = yf.Ticker(self.ticker)
            self.info = tkr.info
        except Exception as e:
            print(f"Error fetching data for {self.ticker}: {e}")
            self.info = {}

    @property
    def p_e_ratio(self):
        """
        Returns P/E ratio (Trailing, Forward, or Default High Value).
        """
        p_e = 100000

        try:
            if cyf.trailingPE in self.info and self.info[cyf.trailingPE] is not None:
                p_e = self.info[cyf.trailingPE]
            elif cyf.forwardPE in self.info and self.info[cyf.forwardPE] is not None:
                p_e = self.info[cyf.forwardPE]

            if isinstance(p_e, (int, float)):
                return round(p_e, 1)
            return 100000

        except Exception:
            return 10000

    @property
    def insider_ownership(self):
        """
        Returns Insider Ownership percentage or 0.
        """
        try:
            val = self.info.get(cyf.heldPercentInsiders, 0)

            if isinstance(val, (int, float)):
                return round(val, 2)
            return 0
        except Exception:
            return 0

    @property
    def free_cashflow(self):
        """
        Returns Free Cash Flow or 0.
        """
        try:
            val = self.info.get(cyf.freeCashflow, 0)
            if isinstance(val, (int, float)):
                return round(val, 0) # Round to nearest whole number
            return 0
        except Exception:
            return 0

    @property
    def market_cap(self):
        """
        Returns Market Capitalization or 0.
        """
        try:
            val = self.info.get(cyf.marketCap, 0)
            if isinstance(val, (int, float)):
                return round(val, 0) # Round to nearest whole number
            return 0
        except Exception:
            return 0

    @property
    def enterprise_to_ebitda(self):
        """
        Returns Enterprise Value to EBITDA ratio or 0.
        """
        try:
            val = self.info.get(cyf.enterpriseToEbitda, 0)
            if isinstance(val, (int, float)):
                return round(val, 2)
            return 0
        except Exception:
            return 0

    def get_all_metrics(self):
        """
        Helper to return a dictionary of all calculated metrics
        for easy DataFrame creation.
        """
        return {
            gv.P_E_RATIO: self.p_e_ratio,
            gv.INSIDER_OWNERSHIP: self.insider_ownership,
         #   gv.FREE_CASHFLOW: self.free_cashflow,
            gv.MARKET_CAP: self.market_cap,
            gv.ENTERPRISE_TO_EBITDA: self.enterprise_to_ebitda
        }

if __name__ == "__main__":
    all_metrics = YahooFinanceTickerInfo("GAMB").get_all_metrics()
    print(all_metrics)