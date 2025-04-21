# === app.py ===

import streamlit as st
import pandas as pd
from datetime import datetime
from config import EXCEL_FILE, TICKER_REPLACEMENTS, POSITION_MAP
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === Streamlit page config ===
st.set_page_config(layout="wide")

# === Sidebar refresh ===
st.sidebar.button("🔄 Refresh Leaderboard")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === Load settings ===
settings_dict = load_settings(EXCEL_FILE)
raw_date = settings_dict.get("start_date", "2025-03-24")
purchase_date = pd.to_datetime(raw_date).date()
TOTAL_CAPITAL = float(settings_dict.get("initial_capital", 5000))
BENCHMARK_TICKER = settings_dict.get("benchmark", "SPY").strip().upper()

# === Header ===
st.markdown("""
    <h1 style='display: flex; align-items: center;'>
        📊 2025 Junior Stock Fantasy League
    </h1>
""", unsafe_allow_html=True)
st.markdown(f"<h4>📅 Start date: <b>{purchase_date}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Return Basis & DRIP Toggles ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)
use_adj_close = st.radio("Use Adjusted Close (DRIP)?", ["Yes", "No"], index=0, horizontal=True) == "Yes"

# === Load roster and parse ===
roster_df = load_roster(EXCEL_FILE)
shares_held, all_tickers, ticker_to_player, ticker_to_direction = parse_roster(
    roster_df, TOTAL_CAPITAL, POSITION_MAP, TICKER_REPLACEMENTS
)

# === Fetch data ===
ticker_metadata = fetch_metadata(all_tickers)
df_prices = fetch_prices(set(all_tickers).union({BENCHMARK_TICKER}), purchase_date, use_adj_close)

# === Compute returns ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    shares_held, df_prices, ticker_metadata, ticker_to_player, ticker_to_direction,
    return_basis, purchase_date, TOTAL_CAPITAL, BENCHMARK_TICKER
)

# === Display visuals ===
show_leaderboard(df_results, player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)

if players_with_missing_data:
    st.warning("Some players have missing stock data. Please refresh later. Affected: " + ", ".join(sorted(players_with_missing_data)))
