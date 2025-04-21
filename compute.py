import pandas as pd

def compute_all_returns(shares_held, df_prices, ticker_metadata, purchase_date, return_basis, TOTAL_CAPITAL):
    results = []
    players_with_missing_data = set()
    portfolio_returns = pd.DataFrame()
    daily_changes = {}
    prices_by_date = {}

    for player, positions in shares_held.items():
        series_list = []
        for ticker, (capital, direction) in positions.items():
            try:
                df = df_prices[ticker].dropna()
                df.index = df.index.date
                df = df[df.index >= purchase_date]
                if df.empty or purchase_date not in df.index:
                    continue

                open_price = df.loc[purchase_date]["Open"]
                close_idx = -2 if return_basis == "Previous Close" and len(df) >= 2 else -1
                close_price = df.iloc[close_idx]["Close"]

                df_return = ((df["Close"] - open_price) / open_price * 100) * direction
                df_return.name = player
                series_list.append(df_return)

                shares = capital / open_price
                shares_held[player][ticker] = shares * direction
                prices_by_date[ticker] = df["Close"]

                raw_return = (close_price - open_price) / open_price
                adj_return = raw_return * direction
                value_now = capital * (1 + adj_return)

                results.append({
                    "Company": ticker_metadata[ticker]["Company"],
                    "Industry": ticker_metadata[ticker]["Industry"],
                    "Player": player,
                    "Purchase Price": round(open_price),
                    "Current Price": round(close_price),
                    "Value ($)": round(value_now),
                    "Return (%)": round(adj_return * 100, 2),
                })
            except:
                players_with_missing_data.add(player)

        if series_list:
            portfolio_returns[player] = pd.concat(series_list, axis=1).mean(axis=1)

    # Daily change % per ticker
    for ticker in df_prices.columns.levels[0]:
        try:
            close_series = df_prices[ticker]["Close"].dropna()
            if len(close_series) >= 2:
                change = ((close_series.iloc[-1] - close_series.iloc[-2]) / close_series.iloc[-2]) * 100
                daily_changes[ticker] = round(change, 2)
        except:
            continue

    # Build dataframe
    df_results = pd.DataFrame(results)

    # Add daily change column
    ticker_to_company = {v["Company"]: k for k, v in ticker_metadata.items()}
    df_results["Daily Change (%)"] = df_results["Company"].map(
        lambda name: daily_changes.get(ticker_to_company.get(name, ""), None)
    )

    # Compute summary
    player_summary = (
        df_results.groupby("Player")["Value ($)"]
        .sum()
        .reset_index()
        .assign(**{
            "Portfolio Value ($)": lambda df: df["Value ($)"].round(),
            "Return (%)": lambda df: ((df["Value ($)"] - TOTAL_CAPITAL) / TOTAL_CAPITAL * 100).round(2)
        })
        .sort_values("Return (%)", ascending=False)
        .reset_index(drop=True)
    )

    return df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data