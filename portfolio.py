# portfolio.py

from config import TICKER_REPLACEMENTS, POSITION_MAP

def parse_positions(roster_df, total_capital, position_map=POSITION_MAP, ticker_replacements=TICKER_REPLACEMENTS):
    shares_held = {}
    all_tickers = set()
    ticker_to_player = {}
    ticker_to_direction = {}
    positions = {}

    for _, row in roster_df.iterrows():
        player = row[0]
        raw_ticker = str(row[1]).strip().upper()
        pos_raw = row[2]
        capital = row[3]

        # Replace known tickers (e.g., BRK.B → BRK-B)
        ticker = ticker_replacements.get(raw_ticker, raw_ticker)

        # Parse position direction (handle missing or numeric)
        if isinstance(pos_raw, str):
            direction = position_map.get(pos_raw.strip().upper(), 1)
        elif isinstance(pos_raw, (int, float)):
            direction = 1 if pos_raw >= 0 else -1
        else:
            direction = 1

        shares = (capital * direction) / 1_000_000 * total_capital
        shares_held[ticker] = shares
        all_tickers.add(ticker)
        ticker_to_player[ticker] = player
        ticker_to_direction[ticker] = direction
        positions[ticker] = (shares, capital, direction)

    return shares_held, all_tickers, ticker_to_player, ticker_to_direction, positions