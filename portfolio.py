# portfolio.py

def parse_positions(roster_df, total_capital, position_map, ticker_replacements):
    """
    Parses a DataFrame of positions and returns shares held, all tickers,
    and mappings from ticker to player and direction.

    Args:
        roster_df (pd.DataFrame): DataFrame with columns [Player, Ticker, Direction, Capital].
        total_capital (float): Total portfolio capital in dollars.
        position_map (dict): Mapping from textual directions to numeric (+1/-1).
        ticker_replacements (dict): Mapping from incorrect tickers to corrected ones.

    Returns:
        dict: shares_held
        set: all_tickers
        dict: ticker_to_player
        dict: ticker_to_direction
    """
    shares_held = {}
    all_tickers = set()
    ticker_to_player = {}
    ticker_to_direction = {}

    for _, row in roster_df.iterrows():
        player = row[0]
        raw_ticker = str(row[1]).strip().upper()
        pos_raw = row[2]
        capital = row[3]

        # Standardize ticker
        ticker = ticker_replacements.get(raw_ticker, raw_ticker)

        # Interpret direction
        if isinstance(pos_raw, str):
            direction = position_map.get(pos_raw.strip().upper(), 1)
        elif isinstance(pos_raw, (int, float)):
            direction = 1 if pos_raw >= 0 else -1
        else:
            direction = 1

        # Safely convert capital to float
        try:
            capital_value = float(capital)
        except Exception:
            capital_value = 0.0

        # Convert from millions to dollars and apply direction
        shares = (capital_value * direction) / 1_000_000 * total_capital

        # Store values
        shares_held[ticker] = shares
        all_tickers.add(ticker)
        ticker_to_player[ticker] = player
        ticker_to_direction[ticker] = direction

    return shares_held, all_tickers, ticker_to_player, ticker_to_direction