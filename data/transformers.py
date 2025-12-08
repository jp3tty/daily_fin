import pandas as pd 
import streamlit as st

@st.cache_data
def create_merged_df(_df_mom, _df_eng):
    """Merge momentum and engulfing dataframes"""
    col_rename_mom = {
        'Scraped_At': 'Scraped_At_Mom',
        'RSI': 'RSI_Mom',
        'Momentum': 'Momentum_Mom',
        'Momentum_Strength_Pct': 'Momentum_Strength_Pct_Mom',
        'Current_Trend': 'Current_Trend_Mom',
        'Signal_Strength': 'Signal_Strength_Mom',
        'Bullish_Days_30d': 'Bullish_Days_30d_Mom',
        'Bearish_Days_30d': 'Bearish_Days_30d_Mom',
    }
    
    col_rename_eng = {
        'Scraped_At': 'Scraped_At_Eng',
        'Latest_Signal_Name': 'Latest_Signal_Name_Eng',
        'Latest_Close': 'Latest_Close_Eng',
        'Bearish_Count_90d': 'Bearish_Count_90d_Eng',
        'Bullish_Count_90d': 'Bullish_Count_90d_Eng',
    }
    
    df_mom = _df_mom.rename(columns=col_rename_mom).drop('No.', axis=1, errors='ignore')
    df_eng = _df_eng.rename(columns=col_rename_eng).drop('No.', axis=1, errors='ignore')
    
    # Merge on common columns
    merged_df = pd.merge(
        df_eng, df_mom, 
        how='left', 
        on=['Ticker', 'Market Cap', 'P/E', 'Fwd P/E', 'PEG', 'P/S', 'P/B',
            'P/C', 'P/FCF', 'EPS This Y', 'EPS Next Y', 'EPS Past 5Y',
            'EPS Next 5Y', 'Sales Past 5Y', 'Price', 'Change', 'Volume']
    )

    display_cols = ['Ticker', 'Latest_Close_Eng', 'Latest_Signal_Name_Eng',
                    'Current_Trend_Mom', 'Signal_Strength_Mom']
    merged_df = merged_df[display_cols]
    merged_df = merged_df.rename(columns={'Latest_Close_Eng': 'Latest Close',
                                          'Latest_Signal_Name_Eng': 'Engulfing Signal',
                                          'Current_Trend_Mom': 'Momentum Trend',
                                          'Signal_Strength_Mom': 'Momentum Strength'})

    # Round "Latest Close" to 2 decimal places
    merged_df['Latest Close'] = merged_df['Latest Close'].astype(float).round(2)

    return merged_df.sort_values(by='Ticker', ascending=True)