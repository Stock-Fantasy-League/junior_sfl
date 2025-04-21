import streamlit as st

def show_leaderboard(df_results):
    st.subheader("📋 Position Leaderboard")

    # Sort the leaderboard
    df_sorted = df_results.sort_values("Return (%)", ascending=False).reset_index(drop=True)
    df_sorted.index += 1

    # Determine global min/max for heatmap consistency
    return_min = df_results["Return (%)"].min()
    return_max = df_results["Return (%)"].max()
    daily_min = df_results["Daily Change (%)"].min()
    daily_max = df_results["Daily Change (%)"].max()

    # Top and Bottom 5 tables
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏆 Top 5 Positions")
        top5 = df_sorted.head(5)[["Company", "Player", "Return (%)", "Daily Change (%)"]]
        st.dataframe(
            top5.style
            .format({"Return (%)": "{:.2f}", "Daily Change (%)": "{:.2f}"})
            .background_gradient(subset=["Return (%)"], cmap="RdYlGn", vmin=return_min, vmax=return_max)
            .background_gradient(subset=["Daily Change (%)"], cmap="RdBu", vmin=daily_min, vmax=daily_max),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("### 💥 Bottom 5 Positions")
        bottom5 = df_sorted.tail(5)[["Company", "Player", "Return (%)", "Daily Change (%)"]]
        st.dataframe(
            bottom5.style
            .format({"Return (%)": "{:.2f}", "Daily Change (%)": "{:.2f}"})
            .background_gradient(subset=["Return (%)"], cmap="RdYlGn", vmin=return_min, vmax=return_max)
            .background_gradient(subset=["Daily Change (%)"], cmap="RdBu", vmin=daily_min, vmax=daily_max),
            use_container_width=True,
            hide_index=True
        )

    # Full leaderboard table
    st.markdown("### 📋 Full Position Table")
    col_order = [
        "Company", "Industry", "Player",
        "Purchase Price", "Current Price", "Value ($)",
        "Return (%)", "Daily Change (%)"
    ]
    full = df_sorted[col_order]
    st.dataframe(
        full.style
        .format({"Return (%)": "{:.2f}", "Daily Change (%)": "{:.2f}"})
        .background_gradient(subset=["Return (%)"], cmap="RdYlGn", vmin=return_min, vmax=return_max)
        .background_gradient(subset=["Daily Change (%)"], cmap="RdBu", vmin=daily_min, vmax=daily_max),
        use_container_width=True
    )