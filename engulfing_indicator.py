import pandas as pd 
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# === FUNCTIONS (importable) ===

def Revsignal1(df1):
    """
    Detect engulfing patterns
    Returns: 0 = no pattern, 1 = bearish engulfing, 2 = bullish engulfing
    """
    length = len(df1) 
    high = list(df1['High'])
    low = list(df1['Low'])
    close = list(df1['Close'])
    open_price = list(df1['Open'])
    signal = [0]*length
    bodydiff = [0]*length

    # Minimum body size threshold (0.3% of price)
    bodydiffmin = 0.003

    for row in range(1, length):
        bodydiff[row] = abs(open_price[row] - close[row])
        bodydiff[row-1] = abs(open_price[row-1] - close[row-1])
        
        if (bodydiff[row] > bodydiffmin and bodydiff[row-1] > bodydiffmin and 
            open_price[row-1] < close[row-1] and    # Previous candle is bullish 
            open_price[row] > close[row] and        # Current candle is bearish
            open_price[row] >= close[row-1] and     # Current open >= previous close
            close[row] <= open_price[row-1]):       # Current close <= previous open
            signal[row] = 1                         # Bearish engulfing

        elif (bodydiff[row] > bodydiffmin and bodydiff[row-1] > bodydiffmin and
            open_price[row-1] > close[row-1] and    # Previous candle is bearish
            open_price[row] < close[row] and        # Current candle is bullish
            open_price[row] <= close[row-1] and     # Current open <= previous close
            close[row] >= open_price[row-1]):       # Current close >= previous open
            signal[row] = 2                         # Bullish engulfing
        else:
            signal[row] = 0                         # Neutral pattern

    return signal

def analyze_ticker_patterns(symbol, stock_data_df):
    """Analyze ticker data for engulfing patterns"""
    try:
        ticker_df = stock_data_df[stock_data_df['Ticker'] == symbol].copy()
        
        if ticker_df.empty:
            return None

        ticker_df = ticker_df.sort_values('Date').reset_index(drop=True)
        ticker_df['Signal'] = Revsignal1(ticker_df)

        latest_signal = ticker_df['Signal'].iloc[-1]
        latest_date = ticker_df['Date'].iloc[-1]
        bearish_count = (ticker_df['Signal'] == 1).sum()
        bullish_count = (ticker_df['Signal'] == 2).sum()
        latest_close = ticker_df['Close'].iloc[-1]

        return {
            'Ticker': symbol,
            'Latest_Signal': latest_signal,
            'Latest_Date': latest_date,
            'Bearish_Count': bearish_count,
            'Bullish_Count': bullish_count,
            'Latest_Close': latest_close,
            'Data': ticker_df
        }

    except Exception as e:
        logging.warning(f"Error analyzing {symbol}: {str(e)}")
        return None 

def run_engulfing_analysis():
    """Main analysis workflow"""
    # Load FinViz data
    finviz_df = pd.read_csv('saved_data/FinVizData.csv') 
    symbol_list = finviz_df['Ticker'].unique().tolist()

    # Load stock candle data
    try:
        stock_data = pd.read_csv('saved_data/stock_candles_90d.csv')
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    except FileNotFoundError:
        logging.error("saved_data/stock_candles_90d.csv not found")
        exit(1)

    logging.info(f"Analyzing {len(symbol_list)} tickers for engulfing patterns")

    results = []
    for symbol in symbol_list:
        result = analyze_ticker_patterns(symbol, stock_data)
        if result:
            results.append({
                'Ticker': result['Ticker'],
                'Latest_Signal': result['Latest_Signal'],
                'Latest_Signal_Name': {0: 'Neutral', 1: 'Bearish', 2: 'Bullish'}[result['Latest_Signal']],
                'Latest_Date': result['Latest_Date'],
                'Bearish_Count_90d': result['Bearish_Count'],
                'Bullish_Count_90d': result['Bullish_Count'],
                'Latest_Close': result['Latest_Close']
            })

    pattern_df = pd.DataFrame(results).sort_values(['Latest_Signal', 'Latest_Close'], ascending=False)

    # Merge with FinViz data
    merged_df = finviz_df.merge(
        pattern_df[['Ticker', 'Latest_Signal_Name', 'Latest_Close', 'Bearish_Count_90d', 'Bullish_Count_90d']], 
        on='Ticker', 
        how='left'
    )

    # Save to CSV
    merged_df.to_csv('saved_data/FinVizData_with_engulfing_patterns.csv', index=False)
    logging.info(f"Saved {len(results)} results to FinVizData_with_engulfing_patterns.csv")

# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    run_engulfing_analysis()
