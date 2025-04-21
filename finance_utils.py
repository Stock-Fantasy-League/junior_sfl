import streamlit as st
import yfinance as yf

@st.cache_data(ttl=3600)
def fetch_metadata(tickers):
    meta = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            company_name = info.get("shortName", "").strip()
            industry = info.get("industry", "Unknown")

            # Use fallback only if shortName is missing or same as ticker
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
def fetch_prices(tickers, start_date):
    data = yf.download(list(tickers), start=start_date, progress=False, group_by="ticker")

    # Identify which tickers failed
    try:
        downloaded = set(data.columns.levels[0])
    except:
        downloaded = set()

    missing = set(tickers) - downloaded
    if missing:
        st.warning(f"⚠️ These tickers failed to download from Yahoo Finance: {', '.join(sorted(missing))}")

    return data