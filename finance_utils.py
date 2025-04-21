import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_metadata(tickers, _trigger=None):
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
        except:
            meta[t] = {
                "Company": f"[{t}]",
                "Industry": "Unknown"
            }
    return meta

@st.cache_data(ttl=3600)
def fetch_prices(tickers, start_date, _trigger=None):
    return yf.download(list(tickers), start=start_date, progress=False, group_by="ticker")