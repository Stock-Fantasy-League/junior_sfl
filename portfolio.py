# portfolio.py

def parse_positions(roster, position_map, replacements, total_capital):
    shares_held = {}
    positions_dict = {}
    ticker_to_player = {}
    ticker_to_direction = {}
    all_tickers = set()

    for _, row in roster.iterrows():
        player = row["Player"]
        positions = []

        for i in range(1, 6):
            raw_ticker = str(row.get(f"Stock {i}", "")).strip().upper()
            pos_raw = str(row.get(f"Position {i}", "")).strip().upper()
            if not raw_ticker:
                continue
            ticker = replacements.get(raw_ticker, raw_ticker)
            direction = position_map.get(pos_raw, 1)
            positions.append((ticker, direction))
            ticker_to_player[ticker] = player
            ticker_to_direction[ticker] = direction
            all_tickers.add(ticker)

        if positions:
            capital_per_position = total_capital / len(positions)
            shares_held[player] = {}
            positions_dict[player] = {}

            for ticker, direction in positions:
                shares_held[player][ticker] = (capital_per_position, direction)
                positions_dict[player][ticker] = (capital_per_position, direction)

    return shares_held, positions_dict, ticker_to_player, ticker_to_direction, all_tickers