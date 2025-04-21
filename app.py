import streamlit as st
import pandas as pd
from datetime import datetime

from config import EXCEL_FILE
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === MUST BE FIRST STREAMLIT COMMAND ===
st.set_page_config(layout="wide")

# === Load settings ===
settings = load_settings()
raw_date = settings.get("start_date", "2025-03-24")
purchase_date = pd.to_datetime(str(raw_date).strip(), errors="coerce").date()
purchase_date_str = purchase_date.isoformat()
TOTAL_CAPITAL = float(settings.get("initial_capital", 5000))
BENCHMARK_TICKER = settings.get("benchmark", "SPY").strip().upper()

# === App layout ===
st.sidebar.button("🔄 Refresh Leaderboard")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("""
    <h1 style='display: flex; align-items: center;'>📊 2025 Junior Stock Fantasy League</h1>
""", unsafe_allow_html=True)

st.markdown(f"<h4>📅 Start date: <b>{purchase_date_str}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Toggle options ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)
use_adj_close = st.radio("Use Adjusted Close (DRIP)?", ["Yes", "No"], horizontal=True) == "Yes"

# === Load portfolio data ===
roster = load_roster()
shares_held, all_tickers, ticker_to_player, ticker_to_direction = parse_roster(roster, TOTAL_CAPITAL)

# === Fetch metadata and price data ===
ticker_metadata = fetch_metadata(all_tickers)
df_prices = fetch_prices(all_tickers.union({BENCHMARK_TICKER}), purchase_date, use_adj_close)

# === Compute returns and errors ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    shares_held, df_prices, ticker_metadata, purchase_date, return_basis, TOTAL_CAPITAL
)

# === Show warnings ===
if players_with_missing_data:
    st.warning("Some players have missing data. Affected: " + ", ".join(sorted(players_with_missing_data)))

# === Render Leaderboard ===
show_leaderboard(df_results)

# === Render Performance Tab ===
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)