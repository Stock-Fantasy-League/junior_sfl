# finance_utils.py

import yfinance as yf
import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor

@st.cache_data(ttl=3600)
def fetch_prices(tickers, start_date, use_adj_close):
    """
    Download historical price data for the given tickers.

    Args:
        tickers (set): Set of ticker symbols.
        start_date (date): Start date for historical prices.
        use_adj_close (bool): Whether to include adjusted close prices.

    Returns:
        pd.DataFrame: Price data (MultiIndex with ticker and OHLC/Adj Close).
    """
    try:
        df = yf.download(
            tickers=list(tickers),
            start=start_date,
            group_by="ticker",
            auto_adjust=False,
            progress=False,
            threads=True
        )
        # Keep only relevant columns
        columns_needed = ["Open", "Close"]
        if use_adj_close:
            columns_needed.append("Adj Close")
        df = df.loc[:, df.columns.get_level_values(1).isin(columns_needed)]
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to fetch prices: {e}")

@st.cache_data(ttl=3600)
def fetch_metadata(tickers):
    """
    Concurrently fetch company metadata for each ticker.

    Args:
        tickers (set): Set of ticker symbols.

    Returns:
        dict: Metadata per ticker: {ticker: {"Company": name, "Industry": industry}}
    """
    def get_info(ticker):
        try:
            info = yf.Ticker(ticker).info
            name = info.get("shortName", "").strip()
            industry = info.get("industry", "Unknown")
            if not name or name.upper() == ticker:
                name = f"[{ticker}]"
            return ticker, {"Company": name, "Industry": industry}
        except:
            return ticker, {"Company": f"[{ticker}]", "Industry": "Unknown"}

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(get_info, tickers)

    return dict(results)