import pandas as pd
import yfinance as yf

def compute_all_returns(roster, prices, purchase_date, return_basis, drip, replacements, position_map):
    players_with_missing_data = set()
    player_summary = []
    results = []
    portfolio_returns = pd.DataFrame()
    daily_changes = {}

    # Helper: get clean ticker
    def get_ticker(raw):
        return replacements.get(raw.strip().upper(), raw.strip().upper())

    for _, row in roster.iterrows():
        player = row["Player"]
        positions = []

        for i in range(1, 6):
            raw_ticker = str(row.get(f"Stock {i}", "")).strip()
            pos_raw = str(row.get(f"Position {i}", "")).strip().upper()
            if not raw_ticker:
                continue

            ticker = get_ticker(raw_ticker)
            direction = position_map.get(pos_raw, 1)
            positions.append((ticker, direction))

        if not positions:
            continue

        capital = 5000
        capital_per_position = capital / len(positions)
        series_list = []

        for ticker, direction in positions:
            try:
                df = prices.get(ticker)
                if df is None or df.empty:
                    players_with_missing_data.add(player)
                    continue

                df = df.copy()
                df.index = pd.to_datetime(df.index).date
                df = df[df.index >= purchase_date]

                if purchase_date not in df.index:
                    players_with_missing_data.add(player)
                    continue

                open_price = df.loc[purchase_date]["Open"]
                close_idx = -2 if return_basis == "Previous Close" and len(df) >= 2 else -1
                close_price = df.iloc[close_idx]["Close"]

                shares = capital_per_position / open_price

                if drip:
                    df["Daily Return"] = df["Close"].pct_change().fillna(0)
                    df["Shares"] = shares * (1 + df["Daily Return"]).cumprod()
                    df["Value"] = df["Shares"] * df["Close"]
                    value_now = df["Value"].iloc[close_idx]
                else:
                    value_now = shares * close_price

                raw_return = (value_now - capital_per_position) / capital_per_position
                adj_return = raw_return * direction

                df_return = ((df["Close"] - open_price) / open_price * 100) * direction
                df_return.name = player
                series_list.append(df_return)

                results.append({
                    "Company": ticker,
                    "Player": player,
                    "Purchase Price": round(open_price, 2),
                    "Current Price": round(close_price, 2),
                    "Value ($)": round(value_now, 2),
                    "Return (%)": round(adj_return * 100, 2)
                })

                # Daily change
                if len(df) >= 2:
                    c2, c1 = df["Close"].iloc[-1], df["Close"].iloc[-2]
                    daily_changes[ticker] = round((c2 - c1) / c1 * 100, 2)
            except:
                players_with_missing_data.add(player)

        if series_list:
            portfolio_returns[player] = pd.concat(series_list, axis=1).mean(axis=1)

    df_results = pd.DataFrame(results)

    if df_results.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, set()

    player_summary = (
        df_results.groupby("Player")["Value ($)"]
        .sum()
        .reset_index()
        .assign(**{
            "Portfolio Value ($)": lambda df: df["Value ($)"].round(),
            "Return (%)": lambda df: ((df["Value ($)"] - capital) / capital * 100).round(2)
        })
        .sort_values("Return (%)", ascending=False)
        .reset_index(drop=True)
    )

    return df_results, player_summary, portfolio_returns, daily_changes, players_with_missing_data