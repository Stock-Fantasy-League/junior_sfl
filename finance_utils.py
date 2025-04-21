# === finance_utils.py ===

import yfinance as yf

@st.cache_data(ttl=3600)
def fetch_metadata(tickers):
    meta = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).info
            name = info.get("shortName", t).strip()
            if not name or name.upper() == t:
                name = f"[{t}]"
            meta[t] = {
                "Company": name,
                "Industry": info.get("industry", "Unknown")
            }
        except:
            meta[t] = {"Company": f"[{t}]", "Industry": "Unknown"}
    return meta

@st.cache_data(ttl=3600)
def fetch_prices(tickers, start_date, use_adj_close):
    return yf.download(list(tickers), start=start_date, progress=False, group_by="ticker")

