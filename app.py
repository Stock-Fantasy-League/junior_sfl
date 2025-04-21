import streamlit as st
from datetime import datetime
from config import EXCEL_FILE
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard  # Only importing leaderboard visuals

# === App layout ===
st.set_page_config(layout="wide")
st.sidebar.button("Refresh Leaderboard")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("""
    <h1 style='display: flex; align-items: center;'>
        📊 2025 Junior Stock Fantasy League
    </h1>
""", unsafe_allow_html=True)

# === Load settings ===
settings = load_settings()
raw_date = settings.get("start_date", "2025-03-24")
purchase_date_str = raw_date
purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
TOTAL_CAPITAL = float(settings.get("initial_capital", 5000))
BENCHMARK_TICKER = settings.get("benchmark", "SPY").strip().upper()

st.markdown(f"<h4>🗓️ Start date: <b>{purchase_date_str}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Return basis toggle ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)

# === Load data ===
roster = load_roster()
shares_held, all_tickers, ticker_to_player, ticker_to_direction = parse_roster(roster, TOTAL_CAPITAL)

ticker_metadata = fetch_metadata(all_tickers)
df_prices = fetch_prices(all_tickers.union({BENCHMARK_TICKER}), purchase_date)

# === Compute returns and daily changes ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    shares_held, df_prices, ticker_metadata, purchase_date, return_basis, TOTAL_CAPITAL
)

# === Warning for missing data ===
if players_with_missing_data:
    st.warning("Some players have missing stock data. Their returns may be inaccurate. Please refresh the leaderboard. Players affected: " + ", ".join(sorted(players_with_missing_data)))

# === Render visuals ===
show_leaderboard(df_results)