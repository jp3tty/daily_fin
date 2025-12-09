import pandas as pd 
import numpy as np
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# === FUNCTIONS (importable) ===

def calculate_rsi(data, periods=14):
    """Calculate Relative Strength Index"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_momentum(data, periods=10):
    """Calculate Price Momentum"""
    return data.diff(periods)

def identify_momentum_trend(df):
    """
    Identify momentum trends in the data 
    Returns df with momentum indicators and trend signals
    """
    df['rsi'] = calculate_rsi(df['close'], periods=14)
    df['momentum'] = calculate_momentum(df['close'], periods=10)
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean() 

    df['price_change'] = df['close'].pct_change() * 100
    df['momentum_strength'] = df['momentum'] / df['close'] * 100 

    df['bullish_momentum'] = (
        (df['rsi'] > 50) & 
        (df['close'] > df['sma_20']) & 
        (df['sma_20'] > df['sma_50']) & 
        (df['momentum'] > 0)
    )

    df['bearish_momentum'] = (
        (df['rsi'] < 50) & 
        (df['close'] < df['sma_20']) & 
        (df['sma_20'] < df['sma_50']) & 
        (df['momentum'] < 0)
    )

    df['strong_bullish'] = (df['rsi'] > 70) | (df['momentum_strength'] > 5)
    df['strong_bearish'] = (df['rsi'] < 30) | (df['momentum_strength'] < -5)

    return df

def analyze_ticker_momentum(symbol, stock_data_df): 
    """Analyze ticker momentum using pre-loaded data"""
    try:
        ticker_df = stock_data_df[stock_data_df['ticker'] == symbol].copy()

        if ticker_df.empty or len(ticker_df) < 50:
            return None 

        ticker_df = ticker_df.sort_values('date').reset_index(drop=True)
        ticker_df = identify_momentum_trend(ticker_df)

        latest = ticker_df.iloc[-1]
        recent_30 = ticker_df.tail(30)

        if latest['bullish_momentum']:
            trend = 'Bullish'
        elif latest['bearish_momentum']:
            trend = 'Bearish'
        else:
            trend = 'Neutral'
        
        if latest['strong_bullish']:
            strength = 'Strong_Bullish'
        elif latest['strong_bearish']:
            strength = 'Strong_Bearish'
        else:
            strength = 'Normal'

        return {
            'Ticker': symbol,
            'Latest_Close': latest['close'],
            'RSI': latest['rsi'],
            'Momentum': latest['momentum'],
            'Momentum_Strength_Pct': latest['momentum_strength'],
            'SMA_20': latest['sma_20'],
            'SMA_50': latest['sma_50'],
            'Current_Trend': trend,
            'Signal_Strength': strength,
            'Bullish_Days_30d': recent_30['bullish_momentum'].sum(),
            'Bearish_Days_30d': recent_30['bearish_momentum'].sum(),
            'Strong_Bullish_Days_30d': recent_30['strong_bullish'].sum(),
            'Strong_Bearish_Days_30d': recent_30['strong_bearish'].sum(),
        }

    except Exception as e:
        logging.warning(f"Error analyzing {symbol}: {str(e)}")
        return None


def run_momentum_analysis():
    """Main analysis workflow"""
    # Load FinViz data
    finviz_df = pd.read_csv('saved_data/FinVizData.csv')

    # Load stock candle data
    try:
        stock_data = pd.read_csv('saved_data/stock_candles_90d.csv')
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
        stock_data.columns = stock_data.columns.str.lower()
    except FileNotFoundError:
        logging.error("saved_data/stock_candles_90d.csv not found")
        exit(1)

    # Get symbol list from candle data
    symbol_list = stock_data['Ticker'].unique().tolist()

    logging.info(f"Analyzing {len(symbol_list)} tickers for momentum indicators")

    results = []
    for symbol in symbol_list:
        result = analyze_ticker_momentum(symbol, stock_data)
        if result:
            results.append(result)

    momentum_df = pd.DataFrame(results)

    # Merge with FinViz data
    merged_df = momentum_df.merge(
        finviz_df.drop(columns=['No.'], errors='ignore'),
        on='Ticker',
        how='left'
    )

    # Save to CSV
    merged_df.to_csv('saved_data/FinVizData_with_momentum_indicators.csv', index=False)
    logging.info(f"Saved {len(results)} results to FinVizData_with_momentum_indicators.csv")


# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    run_momentum_analysis()
