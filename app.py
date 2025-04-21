import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config import EXCEL_FILE, TICKER_REPLACEMENTS, POSITION_MAP
from data_loader import load_settings, load_roster
from portfolio import parse_roster
from finance_utils import fetch_metadata, fetch_prices
from compute import compute_returns, compute_daily_changes, compute_summary_table
from visuals import show_leaderboard, show_performance_chart

# === Streamlit UI Layout ===
st.set_page_config(layout="wide")
if st.sidebar.button("🔄 Refresh Leaderboard (Real-Time)"):
    st.session_state["refresh"] = True
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === Load Settings and Data ===
settings = load_settings()
roster = load_roster()

raw_date = settings.get("start_date", "2025-03-24")
purchase_date = pd.to_datetime(str(raw_date).strip(), errors="coerce").date()
TOTAL_CAPITAL = float(settings.get("initial_capital", 5000))
BENCHMARK_TICKER = settings.get("benchmark", "SPY").strip().upper()
purchase_date_str = purchase_date.isoformat()

# === App Header ===
st.markdown(f"""
    <h1 style='display: flex; align-items: center;'>📊 2025 Junior Stock Fantasy League</h1>
    <h4>🗓️ Start date: <b>{purchase_date_str}</b></h4>
""", unsafe_allow_html=True)
st.caption("Sorted by return — each position equally weighted. Purchase = market open, return = close price basis.")

# === Return Basis ===
return_basis = st.radio("Return Basis", ["Latest Close", "Previous Close"], horizontal=True)

# === Parse Portfolio ===
shares_held, ticker_to_player, ticker_to_direction, all_tickers = parse_roster(
    roster, TOTAL_CAPITAL, POSITION_MAP, TICKER_REPLACEMENTS
)

# === Fetch Data ===
trigger = datetime.now().isoformat() if st.session_state.get("refresh") else None
ticker_metadata = fetch_metadata(all_tickers, _trigger=trigger)
df_prices = fetch_prices(all_tickers.union({BENCHMARK_TICKER}), (purchase_date - timedelta(days=14)).isoformat(), _trigger=trigger)
if "refresh" in st.session_state:
    del st.session_state["refresh"]

# === Compute Returns ===
df_results, portfolio_returns, players_with_missing_data = compute_returns(
    df_prices, shares_held, ticker_metadata, purchase_date, return_basis, TOTAL_CAPITAL
)

if df_results.empty:
    st.warning("⚠️ No return data available to display.")
    st.stop()

# === Daily Change ===
daily_changes = compute_daily_changes(df_prices)
ticker_to_company = {v["Company"]: k for k, v in ticker_metadata.items()}
df_results["Daily Change (%)"] = df_results["Company"].map(
    lambda name: daily_changes.get(ticker_to_company.get(name, ""), None)
)

# === Player Summary Table ===
player_summary = compute_summary_table(df_results, TOTAL_CAPITAL)

# === Display Missing Data Warning ===
if players_with_missing_data:
    st.warning("Some players have missing stock data. Their returns may be inaccurate. Please refresh the leaderboard. Players affected: " + ", ".join(sorted(players_with_missing_data)))

# === Render Visuals ===
show_leaderboard(df_results)
show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, BENCHMARK_TICKER, purchase_date)