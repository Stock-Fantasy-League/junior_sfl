# app.py

import streamlit as st
from datetime import datetime
import pandas as pd

from config import EXCEL_FILE, POSITION_MAP
from data_loader import load_settings, load_roster
from portfolio import parse_positions
from finance_utils import fetch_prices, fetch_metadata
from compute import compute_all_returns
from visuals import show_leaderboard, show_performance_chart

# === Streamlit Page Setup ===
st.set_page_config(layout="wide")
st.sidebar.button("🔄 Refresh Leaderboard")
st.sidebar.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === Header ===
st.markdown("""
    <h1 style='display: flex; align-items: center;'>
        📊 2025 Junior Stock Fantasy League
    </h1>
""", unsafe_allow_html=True)

# === Load Configuration & Data ===
settings = load_settings(EXCEL_FILE)
roster_df = load_roster(EXCEL_FILE)

purchase_date = pd.to_datetime(str(settings["Start Date"])).date()
purchase_date_str = purchase_date.isoformat()
TOTAL_CAPITAL = float(settings["Total Capital"])
BENCHMARK_TICKER = settings["Benchmark"]

st.markdown(f"<h4>🗓️ Start date: <b>{purchase_date_str}</b></h4>", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close or adjusted close based on toggle.")

# === Return Options ===
col_toggle1, col_toggle2 = st.columns(2)
with col_toggle1:
    return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True).lower()
with col_toggle2:
    use_adj_close = st.radio("Dividend Reinvestment (DRIP)", ["Enabled", "Disabled"], horizontal=True) == "Enabled"

# === Parse Roster & Positions ===
shares_held, all_tickers, _, _ = parse_positions(roster_df, TOTAL_CAPITAL, POSITION_MAP)

# === Fetch Price & Metadata ===
df_prices = fetch_prices(all_tickers.union({BENCHMARK_TICKER}), purchase_date, use_adj_close)
ticker_metadata = fetch_metadata(all_tickers)

# === Compute Returns ===
df_results, player_summary_df, portfolio_returns, daily_changes, players_with_missing_data = compute_all_returns(
    df_prices=df_prices,
    shares_held=shares_held,
    purchase_date=purchase_date,
    TOTAL_CAPITAL=TOTAL_CAPITAL,
    return_basis=return_basis,
    use_adj_close=use_adj_close,
    ticker_metadata=ticker_metadata
)

# === Add Daily Change Column to Results ===
df_results["Daily Change (%)"] = df_results["Company"].map(
    lambda name: daily_changes.get(name, None)
)

# === Display Warnings ===
if not df_results.empty:
    if players_with_missing_data:
        st.warning("⚠️ Some players have missing or invalid data. Affected: " + ", ".join(sorted(players_with_missing_data)))
else:
    st.error("❌ No valid return data available. Check your Excel sheet.")
    st.stop()

# === Show Leaderboard and Charts ===
tab1, tab2 = st.tabs(["📋 Leaderboard", "📈 Performance"])
with tab1:
    show_leaderboard(df_results)
with tab2:
    show_performance_chart(player_summary_df, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)