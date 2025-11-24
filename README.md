# Financial Analysis Tools

A collection of Python tools for stock screening, candlestick pattern detection, and technical analysis.

## Features

### 📊 Stock Screener (`stock_screener.py`)
- Scrapes stock data from FinViz based on custom filters
- Exports data to CSV with timestamps
- Configurable screening criteria for market cap, volume, and performance

### 📈 Candlestick Pattern Analysis (`daily_finder.ipynb`)
- Detects bullish and bullish engulfing patterns
- Analyzes historical price data using yfinance
- Generates pattern statistics over configurable time periods
- Exports merged data with pattern signals

### 📉 Technical Analysis Notebooks
- `candlestick.ipynb` - Candlestick chart visualization
- `engulfing.ipynb` - Engulfing pattern analysis
- `momentum.ipynb` - Momentum indicator analysis

## Requirements

```bash
pip install pandas requests beautifulsoup4 yfinance plotly lxml
```

## Usage

### Stock Screener
```bash
python stock_screener.py
```

### Pattern Detection
Open `daily_finder.ipynb` in Jupyter and run the cells sequentially to:
1. Load FinViz screener data
2. Download historical price data for each ticker
3. Detect engulfing patterns
4. Export results with pattern signals

## Output

- `FinVizData.csv` - Raw screener results
- `FinVizData_with_patterns.csv` - Enriched data with pattern signals and statistics

## License

Personal project - All rights reserved

