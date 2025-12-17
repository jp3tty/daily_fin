import streamlit as st
import pandas as pd 
import requests
from io import StringIO

@st.cache_data(ttl=3600)
def load_data_from_github():
    url_mom = 'https://raw.githubusercontent.com/jp3tty/daily_fin/main/saved_data/FinVizData_with_momentum_indicators.csv'
    url_eng = 'https://raw.githubusercontent.com/jp3tty/daily_fin/main/saved_data/FinVizData_with_engulfing_patterns.csv'
    url_can = 'https://raw.githubusercontent.com/jp3tty/daily_fin/main/saved_data/stock_candles_90d.csv'
    
    response_mom = requests.get(url_mom, headers=headers)
    response_eng = requests.get(url_eng, headers=headers)
    response_can = requests.get(url_can, headers=headers)

    if response_mom.status_code != 200 or response_eng.status_code != 200 or response_can.status_code != 200:
        st.error("Failed to fetch data from GitHub")
        st.stop()
    
    df_mom = pd.read_csv(StringIO(response_mom.text))
    df_eng = pd.read_csv(StringIO(response_eng.text))
    df_can = pd.read_csv(StringIO(response_can.text))
    
    return df_mom, df_eng, df_can