# streamlit_momentum_app.py
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from data.loaders import load_data_from_github
from data.transformers import create_merged_df
from components.charts import plot_momentum_candlestick
from pull_stock_candles import ADDITIONAL_TICKERS

df_mom, df_eng, df_can = load_data_from_github()
merged_df = create_merged_df(df_mom, df_eng)

# Filter table to only show tickers with candle data
tickers_with_candles = df_can['Ticker'].dropna().unique()
merged_df = merged_df[merged_df['Ticker'].isin(tickers_with_candles)]

st.title('📈 Candlestick Pattern Analysis')

st.header("Selected Ticker Table")
monitored_stocks = ", ".join(ADDITIONAL_TICKERS)
st.caption(f"Daily candlestick patterns for stocks with small market cap, relative volume > 2x, and 5-day performance > 5%. "
    f"Select a ticker from the table to view the candlestick chart. This table is updated daily after the market closes. "
    f"{monitored_stocks} are also monitored regardless of the screening criteria. These are stocks of personal interest.")

if merged_df.empty:
    st.error(
        "There are no tickers to show: the merged screener data does not overlap with any tickers in the "
        "candlestick file (`stock_candles_90d.csv`). Re-run the data pipeline and confirm the saved CSVs are "
        "committed to the branch this app loads from."
    )
    st.stop()

gb = GridOptionsBuilder.from_dataframe(merged_df)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=11)
gb.configure_selection(selection_mode='single', use_checkbox=False)
gb.configure_default_column(sortable=True, filter=True)
grid_options = gb.build()

grid_response = AgGrid(
    merged_df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    height=400,
    key="ticker_grid",
)

# CHART SECTION


def _ticker_from_grid_selection(selected_rows, default_series):
    """streamlit-aggrid versions differ: selected_rows may be a DataFrame or a list of row dicts."""
    if selected_rows is None:
        return default_series.iloc[0]
    if isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
        return selected_rows.iloc[0]["Ticker"]
    if isinstance(selected_rows, list) and len(selected_rows) > 0:
        row = selected_rows[0]
        if isinstance(row, dict):
            return row.get("Ticker", default_series.iloc[0])
    return default_series.iloc[0]


selected_ticker = _ticker_from_grid_selection(
    grid_response["selected_rows"],
    merged_df["Ticker"],
)

days_range = st.slider("Date Range (days)", min_value=5, max_value=90, value=20)

fig = plot_momentum_candlestick(selected_ticker, df_can, days=days_range)
if fig is not None:
    st.plotly_chart(fig)
else:
    st.warning(f"No candle data available for {selected_ticker}. This ticker may not have been included in the latest data pull.")