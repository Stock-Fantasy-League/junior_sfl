import streamlit as st
from datetime import datetime
from config import EXCEL_FILE, BENCHMARK_TICKER
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_prices, fetch_metadata
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === Streamlit Setup ===
st.set_page_config(layout="wide")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === Load Settings and Inputs ===
settings = load_settings(EXCEL_FILE)
start_date = settings["start_date"]
initial_capital = settings["initial_capital"]
benchmark = settings.get("benchmark", BENCHMARK_TICKER)

st.markdown("""
    <h1 style='display: flex; align-items: center;'>📊 2025 Junior Stock Fantasy League</h1>
""", unsafe_allow_html=True)
st.markdown(f"<h4>🗓️ Start date: <b>{start_date}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === User Input Controls ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)
use_adj_close = st.toggle("Enable Dividend Reinvestment (DRIP)", value=True)

# === Load Roster and Ticker Info ===
roster = load_roster(EXCEL_FILE)
shares_held, tickers = parse_roster(roster, settings)

# === Fetch Metadata and Prices ===
ticker_metadata = fetch_metadata(tickers)
df_prices = fetch_prices(tickers.union({benchmark}), start_date.isoformat(), use_adj_close=use_adj_close)

# === Compute All Returns and Summary Data ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    shares_held, df_prices, ticker_metadata, start_date, return_basis, initial_capital
)

# === Show Warnings if Any Tickers Fail ===
if players_with_missing_data:
    st.warning("⚠️ Some players have stocks with missing or invalid data (e.g., delisted or rate-limited): " +
               ", ".join(sorted(players_with_missing_data)))

# === Render Visuals ===
show_leaderboard(df_results, daily_changes)
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, benchmark, start_date)