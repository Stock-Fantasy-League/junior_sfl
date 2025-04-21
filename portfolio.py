# portfolio.py

from config import TICKER_REPLACEMENTS, POSITION_MAP

def parse_positions(roster_df, total_capital, position_map=POSITION_MAP):
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

        # Apply any ticker replacements (e.g., BRK.B -> BRK-B)
        ticker = TICKER_REPLACEMENTS.get(raw_ticker, raw_ticker)

        # Handle position direction (LONG/SHORT)
        if isinstance(pos_raw, str):
            direction = position_map.get(pos_raw.strip().upper(), 1)
        else:
            direction = 1  # Default to LONG if missing or invalid

        shares = (capital * direction) / 1_000_000 * total_capital  # Scale to total capital
        positions[ticker] = (shares, capital, direction)

        shares_held[ticker] = shares
        all_tickers.add(ticker)
        ticker_to_player[ticker] = player
        ticker_to_direction[ticker] = direction

    return shares_held, all_tickers, ticker_to_player, ticker_to_direction, positions