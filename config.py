# config.py

EXCEL_FILE = "roster.xlsx"

# Ticker fixes (used in replacements, parsing, etc.)
TICKER_REPLACEMENTS = {
    "BRK.B": "BRK-B",
    "MOG.A": "MOG-A"
}

# Position keywords for direction
POSITION_MAP = {
    "LONG": 1, "+1": 1,
    "SHORT": -1, "-1": -1
}