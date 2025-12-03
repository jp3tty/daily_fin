import pandas as pd 
import numpy as np

# Load FinViz data for metadata (used for merge at the end)
finviz_df = pd.read_csv('saved_data/FinVizData.csv')

# Load pre-downloaded stock candle data
print("Loading stock candle data from CSV...")
try:
    stock_data = pd.read_csv('saved_data/stock_candles_90d.csv')
    # Convert Date column to datetime
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    # Convert column names to lowercase for consistency with existing code
    stock_data.columns = stock_data.columns.str.lower()
    print(f"✅ Loaded {len(stock_data)} rows of stock data for {stock_data['ticker'].nunique()} tickers\n")
except FileNotFoundError:
    print("❌ Error: saved_data/stock_candles_90d.csv not found!")
    print("Please run 'pull_stock_candles.py' first to download the data.")
    exit(1)

# Get ticker list from stock data (includes additional tickers from pull_stock_candles.py)
symbol_list = stock_data['ticker'].unique().tolist()

# # Get the data for analysis
# symbol = 'RCL' 
# months = 1
# end_date = datetime.now()
# start_date = end_date - timedelta(days=months*30)

# # Download data
# df = yf.download(symbol, start=start_date, end=end_date, progress=False)

# # Process data
# df.reset_index(inplace=True)
# if isinstance(df.columns, pd.MultiIndex):
#     df.columns = df.columns.get_level_values(0)

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
    # Calculate momentum indicators
    df['rsi'] = calculate_rsi(df['close'], periods=14)
    df['momentum'] = calculate_momentum(df['close'], periods=10)
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean() 

    # Price change and momentum signals
    df['price_change'] = df['close'].pct_change() * 100
    df['momentum_strength'] = df['momentum'] / df['close'] * 100 

    # Identify trend signals 
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

    # Strong momentum signals
    df['strong_bullish'] = (df['rsi'] > 70) | (df['momentum_strength'] > 5)
    df['strong_bearish'] = (df['rsi'] < 30) | (df['momentum_strength'] < -5)

    return df

def analyze_ticker_momentum(symbol, stock_data_df): 
    """
    Analyze ticker momentum using pre-loaded data

    Args:
        symbol: Stock ticker symbol
        stock_data_df: DataFrame with all stock candle data

    Returns:
        Dictionary with momentum analysis results
    """
    try:
        # Filter data for this ticker
        ticker_df = stock_data_df[stock_data_df['ticker'] == symbol].copy()

        if ticker_df.empty or len(ticker_df) < 50: # Need at least 50 days of data
            return None 

        # Sort by date to ensure proper order
        ticker_df = ticker_df.sort_values('date').reset_index(drop=True)

        # Apply momentum analysis
        ticker_df = identify_momentum_trend(ticker_df)

        # Extract latest values (most recent day)
        latest = ticker_df.iloc[-1]

        # Count recent signals (last 30 days)
        recent_30 = ticker_df.tail(30)

        # Determine current trend
        if latest['bullish_momentum']:
            trend = 'Bullish'
        elif latest['bearish_momentum']:
            trend = 'Bearish'
        else:
            trend = 'Neutral'
        
        # Determine strength
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
        print(f"Error analyzing {symbol}: {str(e)}")
        return None


# Main analysis loop
print(f"Analyzing {len(symbol_list)} tickers for momentum indicators...")

results = []
for i, symbol in enumerate(symbol_list, 1):
    print(f"Processing {i}/{len(symbol_list)}: {symbol}", end='\r')
    result = analyze_ticker_momentum(symbol, stock_data)
    if result:
        results.append(result)

print(f"\nCompleted analysis of {len(results)} tickers!")

# Create dataframe
momentum_df = pd.DataFrame(results)


# Merge with FinViz Data and Export
merged_df = finviz_df.merge(
    momentum_df[['Ticker', 'RSI', 'Momentum', 'Momentum_Strength_Pct',
                 'Current_Trend', 'Signal_Strength', 'Bullish_Days_30d', 'Bearish_Days_30d']],
    on='Ticker',
    how='left'
)

# Save to CSV
merged_df.to_csv('saved_data/FinVizData_with_momentum_indicators.csv', index=False)
print("✅ Merged data saved to 'FinVizData_with_momentum_indicators.csv'")


# Summary Statistics
print("\n" + "="*60)
print("MOMENTUM ANALYSIS SUMMARY")
print("="*60)

# Trend distribution
trend_counts = momentum_df['Current_Trend'].value_counts()
print(f"\nCurrent Trend Distribution:")
for trend, count in trend_counts.items():
    print(f"  {trend}: {count} ({count/len(momentum_df)*100:.1f}%)")

# Signal strength
strength_counts = momentum_df['Signal_Strength'].value_counts()
print(f"\nSignal Strength Distribution:")
for strength, count in strength_counts.items():
    print(f"  {strength}: {count} ({count/len(momentum_df)*100:.1f}%)")

# RSI statistics
print(f"\nRSI Statistics:")
print(f"  Average RSI: {momentum_df['RSI'].mean():.2f}")
print(f"  Overbought (RSI > 70): {(momentum_df['RSI'] > 70).sum()} tickers")
print(f"  Oversold (RSI < 30): {(momentum_df['RSI'] < 30).sum()} tickers")

# Top momentum stocks
print(f"\n" + "-"*60)
print("TOP 10 BULLISH MOMENTUM STOCKS")
print("-"*60)
top_bullish = momentum_df.nlargest(10, 'Momentum_Strength_Pct')[
    ['Ticker', 'RSI', 'Momentum_Strength_Pct', 'Current_Trend']
]
print(top_bullish.to_string(index=False))

print(f"\n" + "-"*60)
print("TOP 10 BEARISH MOMENTUM STOCKS")
print("-"*60)
top_bearish = momentum_df.nsmallest(10, 'Momentum_Strength_Pct')[
    ['Ticker', 'RSI', 'Momentum_Strength_Pct', 'Current_Trend']
]
print(top_bearish.to_string(index=False))

# Strong signals
strong_bulls = momentum_df[momentum_df['Signal_Strength'] == 'Strong_Bullish']
strong_bears = momentum_df[momentum_df['Signal_Strength'] == 'Strong_Bearish']

print(f"\n" + "="*60)
print(f"🟢 Strong Bullish Signals: {len(strong_bulls)} tickers")
print(f"🔴 Strong Bearish Signals: {len(strong_bears)} tickers")
print("="*60)