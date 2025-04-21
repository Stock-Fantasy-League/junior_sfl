# compute.py

import pandas as pd

def compute_all_returns(
    df_prices,
    shares_held,
    all_tickers,
    ticker_to_player,
    ticker_to_direction,
    return_basis,
    use_adj_close,
    benchmark_ticker,
    positions_dict
):
    price_col = "Adj Close" if use_adj_close else "Close"
    df_results = []
    daily_changes = {}
    players_with_missing_data = set()

    for player, player_positions in positions_dict.items():
        player_data = []
        for ticker, (capital, direction) in player_positions.items():
            try:
                prices = df_prices[price_col][ticker].dropna()
                prices.index = pd.to_datetime(prices.index).date

                if len(prices) < 2 or prices.empty:
                    players_with_missing_data.add(player)
                    continue

                purchase_date = prices.index[0]
                open_price = df_prices["Open"][ticker].loc[purchase_date]
                close_idx = -2 if return_basis == "Previous Close" and len(prices) >= 2 else -1
                close_price = prices.iloc[close_idx]

                shares = capital / open_price
                ret = ((close_price - open_price) / open_price) * direction
                value = shares * close_price * direction

                player_data.append({
                    "Player": player,
                    "Ticker": ticker,
                    "Return": round(ret * 100, 2),
                    "Value ($)": round(value, 2),
                    "Purchase Price": round(open_price, 2),
                    "Current Price": round(close_price, 2)
                })

                daily_change = prices.pct_change().fillna(0) * shares * direction
                if player not in daily_changes:
                    daily_changes[player] = daily_change
                else:
                    daily_changes[player] += daily_change

            except Exception as e:
                players_with_missing_data.add(player)
                print(f"⚠️ {player} | {ticker}: {e}")
                continue

        df_results.extend(player_data)

    df_results = pd.DataFrame(df_results)
    player_summary = df_results.groupby("Player").agg(
        Return_Percent=("Return", "mean"),
        Total_Value=("Value ($)", "sum")
    ).reset_index().sort_values("Return_Percent", ascending=False)

    return df_results, player_summary, daily_changes, players_with_missing_data