import pandas as pd
from config import EXCEL_FILE

def load_settings(file_path=EXCEL_FILE):
    settings = pd.read_excel(file_path, sheet_name="Settings")
    return dict(zip(settings["Key"], settings["Value"]))

def load_roster(file_path=EXCEL_FILE):
    return pd.read_excel(file_path, sheet_name="Sheet1")