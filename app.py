import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config import EXCEL_FILE, POSITION_MAP, TICKER_REPLACEMENTS
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === App Layout ===
st.set_page_config(layout="wide")

st.markdown("""
    <h1 style='display: flex; align-items: center;'>
        📊 2025 Junior Stock Fantasy League
    </h1>
""", unsafe_allow_html=True)

# === Load Settings ===
settings_dict = load_settings(EXCEL_FILE)

raw_date = settings_dict.get("start_date", "2025-03-24")
try:
    purchase_date = datetime.strptime(str(raw_date), "%Y-%m-%d").date()
except ValueError:
    purchase_date = pd.to_datetime(str(raw_date)).date()

purchase_date_str = purchase_date.isoformat()
TOTAL_CAPITAL = float(settings_dict.get("initial_capital", 5000))
BENCHMARK_TICKER = settings_dict.get("benchmark", "SPY").strip().upper()

st.markdown(f"<h4>🗓️ Start date: <b>{purchase_date_str}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Toggles ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)
use_adj_close = st.radio("Use Adjusted Close (DRIP)?", ["Yes", "No"], horizontal=True) == "Yes"

# === Load Roster and Parse ===
roster_df = load_roster(EXCEL_FILE)
shares_held, all_tickers, ticker_to_player, ticker_to_direction = parse_roster(
    roster_df, TOTAL_CAPITAL, POSITION_MAP, TICKER_REPLACEMENTS
)

# === Fetch Metadata and Price Data ===
ticker_metadata = fetch_metadata(all_tickers)
df_prices = fetch_prices(all_tickers.union({BENCHMARK_TICKER}), purchase_date, use_adj_close)

# === Compute Returns ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    shares_held,
    ticker_metadata,
    df_prices,
    purchase_date,
    return_basis,
    ticker_to_player,
    ticker_to_direction,
    TOTAL_CAPITAL,
    BENCHMARK_TICKER,
    use_adj_close
)

# === Warnings ===
if df_results.empty:
    st.warning("⚠️ No return data available to display.")
    st.stop()

if players_with_missing_data:
    st.warning("Some players have missing stock data. Their returns may be inaccurate. Please refresh the leaderboard. Players affected: " + ", ".join(sorted(players_with_missing_data)))

# === Render Visuals ===
show_leaderboard(df_results)
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)