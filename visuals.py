# visuals.py

import streamlit as st
import pandas as pd
import plotly.express as px

def show_leaderboard(df_results):
    st.subheader("📋 Position Leaderboard")

    # Sort and reset index
    df_sorted = df_results.sort_values("Return (%)", ascending=False).reset_index(drop=True)
    df_sorted.index += 1

    # Global heatmap scaling
    return_min = df_results["Return (%)"].min()
    return_max = df_results["Return (%)"].max()
    daily_min = df_results["Daily Change (%)"].min()
    daily_max = df_results["Daily Change (%)"].max()

    # Top and bottom 5 positions
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏆 Top 5 Positions")
        top5 = df_sorted.head(5)[["Company", "Player", "Return (%)", "Daily Change (%)"]]
        st.dataframe(
            top5.style
            .format({"Return (%)": "{:.2f}", "Daily Change (%)": "{:.2f}"})
            .background_gradient("RdYlGn", subset=["Return (%)"], vmin=return_min, vmax=return_max)
            .background_gradient("RdBu", subset=["Daily Change (%)"], vmin=daily_min, vmax=daily_max),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("### 💥 Bottom 5 Positions")
        bottom5 = df_sorted.tail(5)[["Company", "Player", "Return (%)", "Daily Change (%)"]]
        st.dataframe(
            bottom5.style
            .format({"Return (%)": "{:.2f}", "Daily Change (%)": "{:.2f}"})
            .background_gradient("RdYlGn", subset=["Return (%)"], vmin=return_min, vmax=return_max)
            .background_gradient("RdBu", subset=["Daily Change (%)"], vmin=daily_min, vmax=daily_max),
            use_container_width=True,
            hide_index=True
        )

    # Full leaderboard
    st.markdown("### 📋 Full Position Table")
    col_order = [
        "Company", "Industry", "Player",
        "Purchase Price", "Current Price", "Value ($)",
        "Return (%)", "Daily Change (%)"
    ]
    full_table = df_sorted[col_order]
    st.dataframe(
        full_table.style
        .format({"Return (%)": "{:.2f}", "Daily Change (%)": "{:.2f}"})
        .background_gradient("RdYlGn", subset=["Return (%)"], vmin=return_min, vmax=return_max)
        .background_gradient("RdBu", subset=["Daily Change (%)"], vmin=daily_min, vmax=daily_max),
        use_container_width=True
    )

def show_performance_chart(player_summary, portfolio_returns, df_prices, return_basis, benchmark_ticker, purchase_date):
    st.subheader("📈 Player Return Comparison")

    fig_bar = px.bar(
        player_summary,
        x="Player",
        y="Return (%)",
        color="Return (%)",
        color_continuous_scale="RdYlGn",
        title="Player Return (%)",
    )
    fig_bar.update_layout(xaxis_title="Player", yaxis_title="Return (%)")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("📈 Return Over Time")
    selected_players = st.multiselect("Select Players", sorted(player_summary["Player"].unique()), default=[])
    show_benchmark = st.checkbox(f"Include Benchmark ({benchmark_ticker})", value=True)

    try:
        return_df = portfolio_returns.reset_index().melt(id_vars="index", var_name="Player", value_name="Return (%)")
        return_df.rename(columns={"index": "Date"}, inplace=True)

        if return_basis == "previous_close":
            if len(portfolio_returns.index) >= 2:
                cutoff_date = portfolio_returns.index[-2]
                return_df = return_df[return_df["Date"] <= cutoff_date]

        combined = return_df[return_df["Player"].isin(selected_players)]

        if show_benchmark and benchmark_ticker in df_prices.columns.levels[0]:
            df_bench = df_prices[benchmark_ticker].dropna()
            df_bench.index = df_bench.index.date
            if purchase_date in df_bench.index:
                base_price = df_bench.loc[purchase_date]["Open"]
                df_bench = df_bench[df_bench.index >= purchase_date]
                series = df_bench["Adj Close" if "Adj Close" in df_bench else "Close"]
                if return_basis == "previous_close" and len(series) >= 2:
                    series = series.iloc[:-1]
                bench_returns = ((series - base_price) / base_price * 100).round(2)
                bench_returns = bench_returns.reset_index()
                bench_returns["Player"] = "Benchmark"
                bench_returns.rename(columns={"index": "Date", series.name: "Return (%)"}, inplace=True)
                combined = pd.concat([bench_returns, combined])

        if not combined.empty:
            fig = px.line(
                combined,
                x="Date",
                y="Return (%)",
                color="Player",
                title="Portfolio Return Over Time (%)",
            )
            fig.for_each_trace(
                lambda t: t.update(line=dict(dash="dash")) if t.name == "Benchmark" else t.update(line=dict(dash="solid"))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select players to display the return chart.")
    except Exception as e:
        st.warning("Could not load performance chart.")
        st.exception(e)