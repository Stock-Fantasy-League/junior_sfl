# compute.py

import pandas as pd

def compute_all_returns(df_prices, shares_held, purchase_date, TOTAL_CAPITAL, return_basis, use_adj_close, BENCHMARK_TICKER):
    """
    Calculate portfolio and individual player returns based on prices and position data.
    """
    price_col = "Adj Close" if use_adj_close else "Close"

    # Determine entry prices
    if return_basis == "open":
        entry_prices = df_prices.loc[purchase_date, "Open"]
    else:
        previous_day = df_prices.index[df_prices.index.get_loc(purchase_date) - 1]
        entry_prices = df_prices.loc[previous_day, price_col]

    current_prices = df_prices[price_col].iloc[-1]

    # Calculate player returns
    player_summary = {}
    daily_changes = {}
    players_with_missing_data = set()

    for player, player_positions in shares_held.items():
        portfolio_value = 0
        portfolio_initial = 0
        player_data = []

        for ticker, shares in player_positions.items():
            if ticker not in df_prices.columns.get_level_values(0):
                players_with_missing_data.add(player)
                continue

            initial_price = entry_prices[ticker]
            current_price = current_prices[ticker]

            value = shares * current_price
            invested = shares * initial_price

            portfolio_value += value
            portfolio_initial += invested

            if ticker not in df_prices.columns:
                continue

            series = df_prices[ticker][price_col] * shares
            player_data.append(series)

        if not player_data:
            players_with_missing_data.add(player)
            continue

        player_df = pd.concat(player_data, axis=1).sum(axis=1)
        daily_return = player_df.pct_change().fillna(0)
        daily_changes[player] = daily_return
        total_return = (portfolio_value - portfolio_initial) / portfolio_initial if portfolio_initial != 0 else 0

        player_summary[player] = {
            "Invested": round(portfolio_initial, 2),
            "Final Value": round(portfolio_value, 2),
            "Return": round(total_return * 100, 2)
        }

    # Benchmark
    benchmark_returns = df_prices[BENCHMARK_TICKER][price_col].pct_change().fillna(0)

    df_results = pd.DataFrame(player_summary).T.sort_values(by="Return", ascending=False)

    return df_results, player_summary, benchmark_returns, daily_changes, players_with_missing_data