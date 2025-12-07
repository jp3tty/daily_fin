import pandas as pd 

# Load FinViz data for metadata (used for merge at the end)
finviz_df = pd.read_csv('saved_data/FinVizData.csv') 
price_df = finviz_df[['Ticker', 'Price']].sort_values(by='Price', ascending=True)

# Load pre-downloaded stock candle data
print("Loading stock candle data from CSV...")
try:
    stock_data = pd.read_csv('saved_data/stock_candles_90d.csv')
    # Convert Date column to datetime
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    print(f"✅ Loaded {len(stock_data)} rows of stock data for {stock_data['Ticker'].nunique()} tickers\n")
except FileNotFoundError:
    print("❌ Error: saved_data/stock_candles_90d.csv not found!")
    print("Please run 'pull_stock_candles.py' first to download the data.")
    exit(1)

# Get ticker list from stock data (includes additional tickers from pull_stock_candles.py)
symbol_list = stock_data['Ticker'].unique().tolist()

# Engulfing pattern detection function
def Revsignal1(df1):
    """
    Detect bearish engulfing patterns
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

# Function to analyze for engulfing patterns
def analyze_ticker_patterns(symbol, stock_data_df):
    """
    Analyze ticker data for engulfing patterns using pre-loaded data

    Args:
        symbol: Stock ticker symbol
        stock_data_df: DataFrame with all stock candle data

    Returns:
        Dictionary with pattern analysis results
    """
    try:
        # Filter data for this ticker
        ticker_df = stock_data_df[stock_data_df['Ticker'] == symbol].copy()
        
        if ticker_df.empty:
            return None

        # Sort by date to ensure proper order
        ticker_df = ticker_df.sort_values('Date').reset_index(drop=True)

        # Apply pattern detection
        ticker_df['Signal'] = Revsignal1(ticker_df)

        # Get most recent signal
        latest_signal = ticker_df['Signal'].iloc[-1]
        latest_date = ticker_df['Date'].iloc[-1]

        # Count patterns in the period
        bearish_count = (ticker_df['Signal'] == 1).sum()
        bullish_count = (ticker_df['Signal'] == 2).sum()

        # Get latest price info
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
        print(f"Error analyzing {symbol}: {str(e)}")
        return None 

# Analyze all tickers from FinViz data
print(f"Analyzing {len(symbol_list)} tickers for engulfing patterns...")

results = []
for i, symbol in enumerate(symbol_list, 1):
    print(f"Processing {i}/{len(symbol_list)}: {symbol}", end='\r')
    result = analyze_ticker_patterns(symbol, stock_data)
    if result:
        results.append({
            'Ticker': result['Ticker'],
            'Latest_Signal': result['Latest_Signal'],
            'Latest_Signal_Name': {0: 'Neutral', 1: 'Bearish', 2: 'Bullish'}[result['Latest_Signal']],
            'Latest_Date': result['Latest_Date'],
            'Bearish_Count_90d': result['Bearish_Count'],
            'Bullish_Count_90d': result['Bulli sh_Count'],
            'Latest_Close': result['Latest_Close']
        })

print(f"\nCompleted analysis of {len(results)} tickers!")

pattern_df = pd.DataFrame(results).sort_values(['Latest_Signal', 'Latest_Close'], ascending=False)
# pattern_df

# Merge pattern data with FinViz metadata (pattern_df as base to include additional_tickers)
merged_df = pattern_df.merge(
    finviz_df, 
    on='Ticker', 
    how='left'
)

# Save to CSV
merged_df.to_csv('saved_data/FinVizData_with_engulfing_patterns.csv', index=False)
print("✅ Merged data saved to 'FinVizData_with_engulfing_patterns.csv'")

# merged_df.head()

# ============================================================
# SUMMARY STATISTICS
# ============================================================

print("\n" + "="*60)
print("PATTERN ANALYSIS SUMMARY")
print("="*60)

# Overall counts
total_analyzed = len(pattern_df)
bearish_latest = len(pattern_df[pattern_df['Latest_Signal'] == 1])
bullish_latest = len(pattern_df[pattern_df['Latest_Signal'] == 2])
neutral_latest = len(pattern_df[pattern_df['Latest_Signal'] == 0])

print(f"\nTotal Tickers Analyzed: {total_analyzed}")
print(f"Latest Signal Distribution:")
print(f"  🔴 Bearish Engulfing: {bearish_latest} ({bearish_latest/total_analyzed*100:.1f}%)")
print(f"  🟢 Bullish Engulfing: {bullish_latest} ({bullish_latest/total_analyzed*100:.1f}%)")
print(f"  ⚪ Neutral: {neutral_latest} ({neutral_latest/total_analyzed*100:.1f}%)")

# 90-day pattern statistics
avg_bearish_90d = pattern_df['Bearish_Count_90d'].mean()
avg_bullish_90d = pattern_df['Bullish_Count_90d'].mean()
total_bearish_90d = pattern_df['Bearish_Count_90d'].sum()
total_bullish_90d = pattern_df['Bullish_Count_90d'].sum()

print(f"\n90-Day Pattern Statistics:")
print(f"  Total Bearish Patterns: {total_bearish_90d} (avg {avg_bearish_90d:.1f} per ticker)")
print(f"  Total Bullish Patterns: {total_bullish_90d} (avg {avg_bullish_90d:.1f} per ticker)")

# Price statistics
avg_price = pattern_df['Latest_Close'].mean()
median_price = pattern_df['Latest_Close'].median()
min_price = pattern_df['Latest_Close'].min()
max_price = pattern_df['Latest_Close'].max()

print(f"\nPrice Statistics:")
print(f"  Average Price: ${avg_price:.2f}")
print(f"  Median Price: ${median_price:.2f}")
print(f"  Range: ${min_price:.2f} - ${max_price:.2f}")

# Top patterns
print(f"\n" + "-"*60)
print("TOP PATTERN ACTIVITY (90 Days)")
print("-"*60)

# Most bearish patterns
most_bearish = pattern_df.nlargest(5, 'Bearish_Count_90d')[['Ticker', 'Bearish_Count_90d', 'Latest_Close']]
print("\n🔴 Top 5 Tickers with Most Bearish Patterns:")
print(most_bearish.to_string(index=False))

# Most bullish patterns
most_bullish = pattern_df.nlargest(5, 'Bullish_Count_90d')[['Ticker', 'Bullish_Count_90d', 'Latest_Close']]
print("\n🟢 Top 5 Tickers with Most Bullish Patterns:")
print(most_bullish.to_string(index=False))

# Latest signals
print(f"\n" + "-"*60)
print("LATEST ENGULFING PATTERNS")
print("-"*60)

bearish_signals = pattern_df[pattern_df['Latest_Signal'] == 1].sort_values('Latest_Date', ascending=False)
if len(bearish_signals) > 0:
    print(f"\n🔴 Tickers with BEARISH Engulfing Pattern (most recent):")
    print(f"Found {len(bearish_signals)} ticker(s)\n")
    print(bearish_signals[['Ticker', 'Latest_Date', 'Latest_Close', 'Bearish_Count_90d']].to_string(index=False))
else:
    print(f"\n🔴 No tickers with bearish engulfing pattern on latest day")

bullish_signals = pattern_df[pattern_df['Latest_Signal'] == 2].sort_values('Latest_Date', ascending=False)
if len(bullish_signals) > 0:
    print(f"\n🟢 Tickers with BULLISH Engulfing Pattern (most recent):")
    print(f"Found {len(bullish_signals)} ticker(s)\n")
    print(bullish_signals[['Ticker', 'Latest_Date', 'Latest_Close', 'Bullish_Count_90d']].to_string(index=False))
else:
    print(f"\n🟢 No tickers with bullish engulfing pattern on latest day")

# Price-based insights
print(f"\n" + "-"*60)
print("PRICE-BASED INSIGHTS")
print("-"*60)

# Low-priced stocks with patterns
low_price_threshold = 10
low_priced = pattern_df[pattern_df['Latest_Close'] < low_price_threshold].sort_values('Latest_Close')
print(f"\nLow-Priced Stocks (< ${low_price_threshold}):")
print(f"Found {len(low_priced)} ticker(s)")
if len(low_priced) > 0:
    print(low_priced[['Ticker', 'Latest_Close', 'Bearish_Count_90d', 'Bullish_Count_90d']].head(10).to_string(index=False))

# High-priced stocks with patterns
high_price_threshold = 100
high_priced = pattern_df[pattern_df['Latest_Close'] > high_price_threshold].sort_values('Latest_Close', ascending=False)
print(f"\nHigh-Priced Stocks (> ${high_price_threshold}):")
print(f"Found {len(high_priced)} ticker(s)")
if len(high_priced) > 0:
    print(high_priced[['Ticker', 'Latest_Close', 'Bearish_Count_90d', 'Bullish_Count_90d']].head(10).to_string(index=False))

print(f"\n" + "="*60)
print("Analysis complete! Check 'FinVizData_with_engulfing_patterns.csv' for full results.")
print("="*60 + "\n")