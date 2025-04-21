import streamlit as st
from datetime import datetime
from config import EXCEL_FILE, TICKER_REPLACEMENTS, POSITION_MAP
from data_loader import load_settings, load_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === Set up Streamlit page ===
st.set_page_config(layout="wide")
st.sidebar.button("🔄 Refresh App")
st.sidebar.caption("Data reloaded from Yahoo Finance on each run")

# === Load data ===
settings_dict = load_settings(EXCEL_FILE)
purchase_date = settings_dict["start_date"]
TOTAL_CAPITAL = float(settings_dict["initial_capital"])
BENCHMARK_TICKER = settings_dict["benchmark"]

roster = load_roster(EXCEL_FILE)

# === Header ===
st.markdown("<h1>📊 2025 Junior Stock Fantasy League</h1>", unsafe_allow_html=True)
st.markdown(f"<h4>📅 Start date: {purchase_date}</h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Return basis toggle ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)

# === DRIP toggle ===
drip = st.radio("Include Dividends?", ["Reinvest (DRIP)", "Price Only"], horizontal=True) == "Reinvest (DRIP)"

# === Process tickers and fetch data ===
all_tickers = set()
for _, row in roster.iterrows():
    for i in range(1, 6):
        raw = str(row.get(f"Stock {i}", "")).strip().upper()
        if raw:
            all_tickers.add(TICKER_REPLACEMENTS.get(raw, raw))

# === Fetch metadata and prices ===
ticker_metadata = fetch_metadata(all_tickers)
df_prices = fetch_prices(all_tickers.union({BENCHMARK_TICKER}), purchase_date)

# === Run full computation ===
df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    roster,
    df_prices,
    purchase_date,
    return_basis,
    drip,
    TICKER_REPLACEMENTS,
    POSITION_MAP
)

# === Visualize ===
show_leaderboard(df_results, daily_changes, TOTAL_CAPITAL, players_with_missing_data)
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)