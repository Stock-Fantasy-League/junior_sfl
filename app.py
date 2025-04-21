import streamlit as st
from config import EXCEL_FILE, TICKER_REPLACEMENTS, POSITION_MAP
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard

# === Set page config FIRST ===
st.set_page_config(layout="wide")

# === Load and parse data ===
settings_dict = load_settings(EXCEL_FILE)
roster = load_roster(EXCEL_FILE)

purchase_date = settings_dict["start_date"]
TOTAL_CAPITAL = float(settings_dict["initial_capital"])
BENCHMARK_TICKER = settings_dict["benchmark"].upper()
purchase_date_str = purchase_date.isoformat()

# === Sidebar refresh + toggles ===
st.sidebar.button("🔁 Refresh App")
st.sidebar.caption("Data reloads from Yahoo Finance on each run")

# === Title and config ===
st.markdown("""
    <h1 style='display: flex; align-items: center;'>
        📊 2025 Junior Stock Fantasy League
    </h1>
""", unsafe_allow_html=True)

st.markdown(f"<h4>📅 Start date: <b>{purchase_date_str}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Return + Dividend toggles ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)
drip_enabled = st.radio("Include Dividends?", ["Reinvest (DRIP)", "Price Only"], horizontal=True) == "Reinvest (DRIP)"

# === Process portfolio ===
players, ticker_metadata, df_prices, errors = parse_roster(roster, TOTAL_CAPITAL, TICKER_REPLACEMENTS, POSITION_MAP)

df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    players, ticker_metadata, df_prices, purchase_date, return_basis, drip_enabled, TOTAL_CAPITAL, BENCHMARK_TICKER
)

# === Leaderboard display ===
show_leaderboard(df_results, daily_changes, players_with_missing_data)
