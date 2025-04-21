# === portfolio.py ===

def parse_roster(roster_df, total_capital, position_map, replacements):
    shares_held = {}
    all_tickers = set()
    ticker_to_player = {}
    ticker_to_direction = {}

    for _, row in roster_df.iterrows():
        player = row["Player"]
        positions = []
        for i in range(1, 6):
            raw_ticker = str(row.get(f"Stock {i}", "")).strip().upper()
            pos_raw = str(row.get(f"Position {i}", "")).strip().upper()
            if not raw_ticker:
                continue
            ticker = replacements.get(raw_ticker, raw_ticker)
            direction = position_map.get(pos_raw, 1)
            ticker_to_player[ticker] = player
            ticker_to_direction[ticker] = direction
            positions.append((ticker, direction))

        if positions:
            shares_held[player] = {}
            capital_per_position = total_capital / len(positions)
            for ticker, direction in positions:
                shares_held[player][ticker] = (capital_per_position, direction)
                all_tickers.add(ticker)

    return shares_held, all_tickers, ticker_to_player, ticker_to_direction

