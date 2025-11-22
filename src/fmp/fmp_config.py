from pathlib import Path
import os

# PATHS
MAIN_DIR = str(Path(__file__).resolve().parents[2])
DATA_DIR = os.path.join(MAIN_DIR, "data")
FMP_DATA_DIR = os.path.join(DATA_DIR, "fmp")



# API KEYS
API_KEY_GMAIL = "W9RU8FWcCeMVliiFWJVfWWseLRrJQV19 "
API_KEY_YAHOO = "lHvVVz6hu9L19T86HWPjS9RyEuW9RZy3"
API_KEY_GMAIL_2 = "lzaXr8HLExNsgXUtT19wRuw3iDQSlZ6A"

assert os.path.isdir(FMP_DATA_DIR)
