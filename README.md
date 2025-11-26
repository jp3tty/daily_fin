# Daily Financial Analysis

Automated stock screening and technical analysis system with GitHub Actions integration.

## 🎯 Overview

This production system automatically:
1. **Scrapes** stock data from FinViz based on custom filters
2. **Analyzes** engulfing candlestick patterns (bullish/bearish signals)
3. **Calculates** momentum indicators (RSI, moving averages, trend signals)
4. **Commits** results to the repository daily after market close

## 📊 Features

### Stock Screener (`stock_screener.py`)
- Scrapes real-time stock data from FinViz
- Configurable screening criteria (market cap, volume, performance)
- Automatic pagination handling
- Built-in rate limiting and error handling
- Saves to `saved_data/FinVizData.csv`

**Current Filters:**
- Market cap: Small cap and above
- Relative volume: Over 2x
- Performance: Up 5%+ today
- Sorted by: Market cap (descending)

### Engulfing Pattern Indicator (`engulfing_indicator.py`)
- Detects bullish and bearish engulfing candlestick patterns
- Analyzes 90 days of historical price data
- Counts pattern frequency and identifies latest signals
- Comprehensive summary statistics and price-based insights
- Saves to `saved_data/FinVizData_with_engulfing_patterns.csv`

**Outputs:**
- Latest signal: Bearish/Bullish/None
- 90-day pattern counts
- Latest closing prices
- Pattern activity summaries
- Price-based filtering (low-priced, high-priced stocks)

### Momentum Indicator (`momentum_indicator.py`)
- Calculates RSI (14-period Relative Strength Index)
- Computes 10-day price momentum
- Tracks SMA-20 and SMA-50 moving averages
- Identifies bullish/bearish momentum trends
- Detects strong signals (overbought/oversold conditions)
- Saves to `saved_data/FinVizData_with_momentum_indicators.csv`

**Outputs:**
- Current trend: Bullish/Bearish/Neutral
- Signal strength: Strong_Bullish/Strong_Bearish/Normal
- RSI values and momentum metrics
- 30-day trend statistics
- Top momentum stocks

## 🤖 Automated Execution

### GitHub Actions Workflow

The system runs automatically via GitHub Actions:

**Schedule:** Weekdays at 4:30 PM EST (after market close)
- Cron: `30 21 * * 1-5` (21:30 UTC)

**Workflow Steps:**
1. Sets up Python 3.11 environment
2. Installs dependencies from `requirements.txt`
3. Creates `saved_data/` directory
4. Runs stock screener
5. Runs engulfing pattern analysis
6. Runs momentum indicator analysis
7. Commits all CSV results to the repository

**Manual Trigger:** You can manually trigger the workflow from the Actions tab in GitHub.

## 📦 Installation

### Requirements

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `requests` - HTTP requests for web scraping
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `yfinance` - Yahoo Finance data

## 🚀 Usage

### Running Locally

```bash
# Create the data directory
mkdir -p saved_data

# Run individual scripts
python stock_screener.py
python engulfing_indicator.py
python momentum_indicator.py
```

### Running All Scripts

```bash
# Run the complete analysis pipeline
python stock_screener.py && \
python engulfing_indicator.py && \
python momentum_indicator.py
```

### Configuration

**Stock Screener:**
Edit the `url` variable in `stock_screener.py` line 114 to customize filters:

```python
url = "https://finviz.com/screener.ashx?v=121&f=cap_smallover,sh_relvol_o2,ta_perf_d5o&ft=4&o=-marketcap"
```

**Analysis Parameters:**
- **Engulfing Indicator:** Modify `days=90` in line 112 to adjust historical lookback
- **Momentum Indicator:** Modify `days=90` in line 151 to adjust historical lookback

## 📂 Output Files

All output files are stored in `saved_data/`:

### `FinVizData.csv`
**Source:** Stock Screener  
**Contains:**
- Ticker symbols
- Market cap, P/E ratios, valuations (P/S, P/B, P/C, P/FCF)
- Growth metrics (EPS, Sales growth)
- Current price, change, volume
- Scraped timestamp

### `FinVizData_with_engulfing_patterns.csv`
**Source:** Engulfing Indicator  
**Contains:**
- All columns from `FinVizData.csv`
- Latest signal name (Bearish/Bullish/None)
- Latest closing price from yfinance
- Bearish pattern count (90-day)
- Bullish pattern count (90-day)

### `FinVizData_with_momentum_indicators.csv`
**Source:** Momentum Indicator  
**Contains:**
- All columns from `FinVizData.csv`
- RSI (14-period)
- 10-day momentum
- Momentum strength percentage
- Current trend (Bullish/Bearish/Neutral)
- Signal strength (Strong_Bullish/Strong_Bearish/Normal)
- Bullish/bearish days count (30-day)

## 📊 Summary Statistics

Each analysis script provides detailed console output:

**Engulfing Patterns:**
- Total tickers analyzed
- Signal distribution percentages
- 90-day pattern totals and averages
- Price statistics
- Top 5 tickers by pattern activity
- Latest engulfing patterns detected
- Low/high-priced stock insights

**Momentum Indicators:**
- Trend distribution (Bullish/Bearish/Neutral)
- Signal strength distribution
- RSI statistics (average, overbought, oversold)
- Top 10 bullish/bearish momentum stocks
- Strong signal counts

## 🔐 Data Protection

**`.gitignore` Configuration:**
- All CSV files are ignored by default
- Exception: CSVs in `saved_data/` are tracked for automated commits
- This prevents accidental commits of test data while allowing workflow outputs

## 📅 Data Freshness

**Automated Updates:**
- Runs Monday-Friday at 4:30 PM EST (after market close)
- Provides same-day analysis with latest market data
- Historical data: 90-day lookback for pattern analysis

**Data Sources:**
- **FinViz:** Real-time screener data
- **Yahoo Finance (yfinance):** Historical OHLC data for technical analysis

## 🛠 Development

This is a **production repository**. Development and experimental work should be done in the parent `dev/` directory.

**Production Standards:**
- ✅ Tested and validated code only
- ✅ Comprehensive error handling
- ✅ Detailed logging
- ✅ Production-ready configuration

## 📈 Use Cases

- **Daily Stock Screening:** Identify high-volume movers
- **Pattern Recognition:** Find bullish/bearish engulfing setups
- **Momentum Trading:** Track RSI and moving average trends
- **Signal Confirmation:** Cross-reference multiple indicators
- **Historical Analysis:** Review 90-day pattern frequency
- **Automated Alerts:** GitHub commit notifications for daily updates

## 🔄 Workflow

```
┌─────────────────────┐
│  GitHub Actions     │
│  (Daily 4:30 PM)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stock Screener     │──► saved_data/FinVizData.csv
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Engulfing Indicator │──► saved_data/FinVizData_with_engulfing_patterns.csv
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Momentum Indicator  │──► saved_data/FinVizData_with_momentum_indicators.csv
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Git Commit        │
│   & Push to Repo    │
└─────────────────────┘
```

## 📝 License

Personal project - All rights reserved

## 🤝 Contributing

This is a personal production repository. Development contributions should be made to the `dev/` directory first.

---

**Last Updated:** 2025-11-26  
**Maintainer:** Jeremy Petty
