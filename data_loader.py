import pandas as pd

def load_settings(file_path):
    """
    Loads the 'Settings' sheet and returns a dictionary of key-value pairs.
    """
    df = pd.read_excel(file_path, sheet_name="Settings")
    return dict(zip(df["Key"], df["Value"]))

def load_roster(file_path):
    """
    Loads the main roster from the first sheet.
    """
    return pd.read_excel(file_path, sheet_name=0)