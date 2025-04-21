import pandas as pd

def compute_all_returns(df_prices, ticker_metadata, shares_held, purchase_date, return_basis):
    results = []
    portfolio_returns = pd.DataFrame()
    daily_changes = {}
    players_with_missing_data = set()

    return_df = {}  # Dictionary to store each player's return time series

    for player, positions in shares_held.items():
        player_returns = []

        for ticker, (capital, direction) in positions.items():
            try:
                df = df_prices[ticker].dropna()
                df.index = df.index.date
                df = df[df.index >= purchase_date]
                if df.empty or purchase_date not in df.index:
                    players_with_missing_data.add(player)
                    continue

                # DRIP: use adjusted close instead of close
                open_price = df.loc[purchase_date]["Open"]
                adj_close_series = df["Adj Close"]

                close_idx = -2 if return_basis == "Previous Close" and len(df) >= 2 else -1
                close_price = df.iloc[close_idx]["Adj Close"]

                raw_return = (close_price - open_price) / open_price
                adj_return = raw_return * direction
                value_now = capital * (1 + adj_return)

                # Compute daily return time series
                df_return = ((adj_close_series - open_price) / open_price * 100) * direction
                df_return.name = player
                player_returns.append(df_return)

                # Add daily change % (most recent 2 adjusted closes)
                if len(adj_close_series) >= 2:
                    daily_change = ((adj_close_series.iloc[-1] - adj_close_series.iloc[-2]) / adj_close_series.iloc[-2]) * 100
                    daily_changes[ticker] = round(daily_change, 2)

                results.append({
                    "Company": ticker_metadata[ticker]["Company"],
                    "Industry": ticker_metadata[ticker]["Industry"],
                    "Player": player,
                    "Purchase Price": round(open_price),
                    "Current Price": round(close_price),
                    "Value ($)": round(value_now),
                    "Return (%)": round(adj_return * 100, 2),
                })

            except Exception as e:
                players_with_missing_data.add(player)

        if player_returns:
            portfolio_returns[player] = pd.concat(player_returns, axis=1).mean(axis=1)

    df_results = pd.DataFrame(results)
    return df_results, portfolio_returns, daily_changes, players_with_missing_data