import streamlit as st
import pandas as pd
from datetime import datetime
from config import EXCEL_FILE
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === Streamlit UI Setup ===
st.set_page_config(layout="wide")
st.sidebar.button("🔄 Refresh Leaderboard")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === Load Settings ===
settings_dict = load_settings(EXCEL_FILE)
raw_date = settings_dict.get("start_date", "2025-03-24")
purchase_date = pd.to_datetime(raw_date).date()
TOTAL_CAPITAL = float(settings_dict.get("initial_capital", 5000))
BENCHMARK_TICKER = settings_dict.get("benchmark", "SPY").strip().upper()
purchase_date_str = purchase_date.isoformat()

# === Header ===
st.markdown("""
    <h1 style='display: flex; align-items: center;'>
        📊 2025 Junior Stock Fantasy League
    </h1>
""", unsafe_allow_html=True)
st.markdown(f"<h4>🗓️ Start date: <b>{purchase_date_str}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Toggles ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)
use_adj_close = st.radio("Use Adjusted Close (DRIP)?", ["Yes", "No"], horizontal=True) == "Yes"

# === Load Data ===
roster_df = load_roster(EXCEL_FILE)
shares_held, all_tickers, ticker_to_player, ticker_to_direction = parse_roster(roster_df, TOTAL_CAPITAL)

# === Fetch Prices & Metadata ===
tickers_to_fetch = all_tickers.union({BENCHMARK_TICKER})
ticker_metadata = fetch_metadata(tickers_to_fetch)
df_prices = fetch_prices(tickers_to_fetch, purchase_date, use_adj_close=use_adj_close)

# === Compute Returns ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    roster_df,
    df_prices,
    purchase_date,
    return_basis,
    TOTAL_CAPITAL,
    ticker_metadata,
    use_adj_close
)

# === Display Warnings ===
if df_results.empty:
    st.warning("⚠️ No return data available to display.")
    st.stop()
if players_with_missing_data:
    st.warning(
        "Some players have missing stock data. Their returns may be inaccurate. "
        f"Affected players: {', '.join(sorted(players_with_missing_data))}"
    )

# === Render Visuals ===
show_leaderboard(df_results)
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)