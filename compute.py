import pandas as pd

def compute_all_returns(df_prices, shares_held, ticker_to_player, ticker_to_direction, purchase_date, return_basis, ticker_metadata, use_adj_close):
    results = []
    portfolio_returns = pd.DataFrame()
    prices_by_date = {}
    players_with_missing_data = set()

    price_col = "Adj Close" if use_adj_close else "Close"

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
                close_price = df.iloc[close_idx][price_col]

                df_return = ((df[price_col] - open_price) / open_price * 100) * direction
                df_return.name = player
                series_list.append(df_return)

                shares = capital / open_price
                shares_held[player][ticker] = shares * direction
                prices_by_date[ticker] = df[price_col]

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

    df_results = pd.DataFrame(results)
    return df_results, portfolio_returns, prices_by_date, players_with_missing_data