import pandas as pd
from config import EXCEL_FILE  # ✅ Import the correct dynamic file path

def load_settings():
    return pd.read_excel(EXCEL_FILE, sheet_name="Settings")

def load_roster():
    return pd.read_excel(EXCEL_FILE, sheet_name="Sheet1")