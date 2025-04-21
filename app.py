# app.py

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from config import EXCEL_FILE, TICKER_REPLACEMENTS, POSITION_MAP
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === Streamlit Page Config (must be first!) ===
st.set_page_config(layout="wide")

# === Load settings and data ===
settings_dict = load_settings(EXCEL_FILE)
raw_date = settings_dict.get("start_date", "2025-03-24")
TOTAL_CAPITAL = float(settings_dict.get("initial_capital", 5000))
BENCHMARK_TICKER = settings_dict.get("benchmark", "SPY").strip().upper()

# Parse date
try:
    purchase_date = datetime.strptime(str(raw_date).strip(), "%Y-%m-%d").date()
except Exception as e:
    st.error(f"❌ Error parsing start date: {raw_date}")
    st.stop()

# === Sidebar and Header ===
st.sidebar.button("🔄 Refresh Leaderboard")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("""
    <h1 style='display: flex; align-items: center;'>📊 2025 Junior Stock Fantasy League</h1>
""", unsafe_allow_html=True)
st.markdown(f"<h4>📅 Start date: <b>{purchase_date.isoformat()}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === User Toggles ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)
use_adj_close = st.radio("Use Adjusted Close (DRIP)?", ["Yes", "No"], horizontal=True) == "Yes"

# === Load roster and parse ===
roster_df = load_roster(EXCEL_FILE)
shares_held, all_tickers, ticker_to_player, ticker_to_direction = parse_roster(
    roster_df, TOTAL_CAPITAL, POSITION_MAP, TICKER_REPLACEMENTS
)

# === Fetch metadata ===
ticker_metadata = fetch_metadata(all_tickers)

# === Fetch price data with DRIP toggle ===
df_prices = fetch_prices(set(all_tickers).union({BENCHMARK_TICKER}), purchase_date, use_adj_close)

# === Calculate returns ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    df_prices, shares_held, ticker_to_player, ticker_to_direction,
    ticker_metadata, TOTAL_CAPITAL, purchase_date, return_basis
)

# === Warning for data gaps ===
if players_with_missing_data:
    st.warning("Some players have missing stock data. Their returns may be inaccurate. Affected players: " + ", ".join(sorted(players_with_missing_data)))

# === Show Visuals ===
show_leaderboard(df_results)
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)