# data_loader.py

import pandas as pd
from config import TICKER_REPLACEMENTS

def load_settings(excel_path):
    """
    Loads competition settings from the 'Settings' sheet in the Excel file.

    Expected columns in sheet: 'Field', 'Value'
    Required fields: 'Start Date', 'Benchmark', 'Total Capital'
    """
    settings_df = pd.read_excel(excel_path, sheet_name="Settings")
    settings_dict = dict(zip(settings_df["Field"], settings_df["Value"]))
    
    # Convert Total Capital to float
    settings_dict["Total Capital"] = float(settings_dict.get("Total Capital", 5000))
    
    # Ensure benchmark is uppercase
    settings_dict["Benchmark"] = str(settings_dict.get("Benchmark", "SPY")).strip().upper()
    
    return settings_dict

def load_roster(excel_path):
    """
    Loads player roster from the 'Roster' sheet in the Excel file.

    Expected columns: Player, Ticker, Position, Capital
    """
    df = pd.read_excel(excel_path, sheet_name="Roster")

    # Normalize ticker names using replacements
    df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()
    df["Ticker"] = df["Ticker"].replace(TICKER_REPLACEMENTS)

    # Strip and uppercase positions
    df["Position"] = df["Position"].astype(str).str.strip().str.upper()

    return df