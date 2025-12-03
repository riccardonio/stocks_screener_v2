import os
from pathlib import Path

# PATHS
MAIN_DIR = str(Path(__file__).resolve().parents[1])
DATA_DIR = os.path.join(MAIN_DIR, "data")

# FILES
ALL_STOCKS_INFO_FILE= os.path.join(DATA_DIR, "finviz", "all_stocks_tickers.csv")

# PARAMETERS NAMES
FCF_YEARS = "fcf_years"
OCF_YEARS = "ocf_years"

# GENERAL
SCORE = "score"
P_E_RATIO = "P_E_ratio"
INSIDER_OWNERSHIP = "insider_ownership"
FREE_CASHFLOW = "Free Cash Flow"
MARKET_CAP = "Market Cap"
ENTERPRISE_TO_EBITDA = "EV/EBITDA"