# portfolio.py

def parse_positions(roster_df, total_capital, position_map):
    """
    Parses a roster DataFrame to calculate shares held per ticker per player.

    Returns:
        shares_held: dict[player][ticker] = number of shares
        all_tickers: set of all tickers across all players
        ticker_to_player: dict[ticker] = player
        ticker_to_direction: dict[ticker] = 1 or -1 depending on long/short
    """
    shares_held = {}
    all_tickers = set()
    ticker_to_player = {}
    ticker_to_direction = {}

    for _, row in roster_df.iterrows():
        player = row["Player"]
        ticker_raw = row["Ticker"]
        pos_raw = row["Position"]
        capital = row["Capital"]

        if pd.isna(ticker_raw) or pd.isna(pos_raw) or pd.isna(capital):
            continue

        # Normalize and validate
        ticker = str(ticker_raw).strip().upper()
        direction = position_map.get(str(pos_raw).strip().upper(), 1)
        capital = float(capital)

        shares = (capital * direction) / 1_000_000 * total_capital

        # Init if not present
        if player not in shares_held:
            shares_held[player] = {}

        shares_held[player][ticker] = shares
        all_tickers.add(ticker)
        ticker_to_player[ticker] = player
        ticker_to_direction[ticker] = direction

    return shares_held, all_tickers, ticker_to_player, ticker_to_direction