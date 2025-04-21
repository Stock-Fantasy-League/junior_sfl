import yfinance as yf
import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def fetch_metadata(tickers):
    meta = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            company_name = info.get("shortName", "").strip()
            industry = info.get("industry", "Unknown")

            if not company_name or company_name.upper() == t:
                company_name = f"[{t}]"

            meta[t] = {
                "Company": company_name,
                "Industry": industry
            }
        except Exception:
            meta[t] = {
                "Company": f"[{t}]",
                "Industry": "Unknown"
            }
    return meta

@st.cache_data(ttl=3600)
def fetch_prices(tickers, start_date, use_adj_close):
    raw = yf.download(list(tickers), start=start_date, progress=False, group_by="ticker")

    if not use_adj_close:
        return raw  # use raw with regular Close and Open

    # Replace Close column with Adj Close if DRIP is enabled
    adj_data = {}
    for ticker in tickers:
        if isinstance(raw.columns, pd.MultiIndex) and ticker in raw.columns.levels[0]:
            ticker_data = raw[ticker].copy()
        else:
            ticker_data = raw.copy()

        if "Adj Close" in ticker_data.columns:
            ticker_data["Close"] = ticker_data["Adj Close"]

        adj_data[ticker] = ticker_data.drop(columns=["Adj Close"], errors="ignore")

    return pd.concat(adj_data, axis=1)