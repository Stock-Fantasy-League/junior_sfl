# config.py

# Excel file path
EXCEL_FILE = "roster.xlsx"

# Standardized replacements for tickers (if needed)
TICKER_REPLACEMENTS = {
    "BRK.B": "BRK-B",
    "MOG.A": "MOG-A"
}

# Mapping for position keywords to numeric directions
POSITION_MAP = {
    "LONG": 1,
    "+1": 1,
    "SHORT": -1,
    "-1": -1
}