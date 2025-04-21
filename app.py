import streamlit as st
import pandas as pd
from datetime import datetime
from config import EXCEL_FILE, TICKER_REPLACEMENTS, POSITION_MAP
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === Must be first Streamlit call ===
st.set_page_config(layout="wide")

# === Sidebar Refresh Button ===
st.sidebar.button("🔄 Refresh Leaderboard")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === Load settings ===
settings_dict = load_settings(EXCEL_FILE)
raw_date = settings_dict.get("start_date", "2025-03-24")

try:
    purchase_date = pd.to_datetime(raw_date).date()
except Exception as e:
    st.error(f"❌ Error parsing start date: {raw_date}")
    st.stop()

purchase_date_str = purchase_date.isoformat()
TOTAL_CAPITAL = float(settings_dict.get("initial_capital", 5000))
BENCHMARK_TICKER = settings_dict.get("benchmark", "SPY").strip().upper()

# === Title & Meta Info ===
st.markdown("""
    <h1 style='display: flex; align-items: center;'>
        📊 2025 Junior Stock Fantasy League
    </h1>
""", unsafe_allow_html=True)

st.markdown(f"<h4>📅 Start date: <b>{purchase_date_str}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Return Basis Toggle ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)

# === DRIP Toggle ===
use_adj_close = st.radio("Use Adjusted Close (DRIP)?", ["Yes", "No"], horizontal=True) == "Yes"

# === Load Roster & Parse Portfolios ===
roster_df = load_roster(EXCEL_FILE)
shares_held, all_tickers, ticker_to_player, ticker_to_direction = parse_roster(
    roster_df, TOTAL_CAPITAL, TICKER_REPLACEMENTS, POSITION_MAP
)

# === Fetch Data ===
ticker_metadata = fetch_metadata(all_tickers)
df_prices = fetch_prices(all_tickers.union({BENCHMARK_TICKER}), purchase_date, use_adj_close)

# === Compute Returns ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    df_prices, shares_held, purchase_date, ticker_metadata, ticker_to_player, ticker_to_direction, return_basis
)

# === Render Visuals ===
show_leaderboard(df_results, daily_changes, players_with_missing_data, TOTAL_CAPITAL)
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)