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
    positions
):
    price_col = "Adj Close" if use_adj_close else "Close"
    df_results = []
    daily_changes = {}
    players_with_missing_data = set()

    for player, player_positions in shares_held.items():
        player_data = []
        for ticker, (shares, direction) in player_positions.items():
            try:
                prices = df_prices[price_col][ticker]
                price_start = prices.iloc[0]
                price_end = prices.iloc[-1] if return_basis == "Latest Close" else prices.iloc[-2]
                ret = ((price_end - price_start) / price_start) * direction
                value = shares * price_end * direction
                player_data.append({
                    "Ticker": ticker,
                    "Return": ret,
                    "Value": value,
                    "Shares": shares,
                    "Start Price": price_start,
                    "End Price": price_end
                })
                daily_change = prices.pct_change().fillna(0) * shares * direction
                if player not in daily_changes:
                    daily_changes[player] = daily_change
                else:
                    daily_changes[player] += daily_change
            except Exception as e:
                players_with_missing_data.add(player)
                print(f"Error processing {ticker} for {player}: {e}")
                continue
        if player_data:
            df_results.extend([
                {
                    "Player": player,
                    **record
                }
                for record in player_data
            ])

    df_results = pd.DataFrame(df_results)
    df_results["Weighted Return"] = df_results["Return"]
    player_summary = df_results.groupby("Player").agg(
        Total_Return=("Weighted Return", "mean"),
        Total_Value=("Value", "sum")
    ).reset_index()
    portfolio_returns = player_summary.sort_values("Total_Return", ascending=False)

    return df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data