# streamlit_momentum_app.py
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from data.loaders import load_data_from_github
from data.transformers import create_merged_df
from components.charts import plot_momentum_candlestick

df_mom, df_eng, df_can = load_data_from_github()
merged_df = create_merged_df(df_mom, df_eng)

st.title('📈 Candlestick Pattern Analysis')

st.header("Selected Ticker Table")
st.caption("Daily candlestick patterns for stocks with market cap ≥ small cap, relative volume > 2x, and 5-day performance > 5%.")

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
    height=400 
)

# CHART SECTION

selected_rows = grid_response['selected_rows']
if selected_rows is not None and len(selected_rows) > 0:
    selected_ticker = selected_rows.iloc[0]['Ticker']
else:
    selected_ticker = merged_df['Ticker'].iloc[0]

fig = plot_momentum_candlestick(selected_ticker, df_can)
st.plotly_chart(fig)