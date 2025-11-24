# Daily Financial Screener

Production-ready stock screening tool for automated FinViz data collection.

## Features

### 📊 Stock Screener (`stock_screener.py`)
- Scrapes stock data from FinViz based on custom filters
- Exports data to CSV with timestamps
- Configurable screening criteria for market cap, volume, and performance
- Automatic pagination handling
- Built-in rate limiting and error handling

## Requirements

```bash
pip install pandas requests beautifulsoup4 lxml
```

## Usage

### Running the Screener

```bash
python stock_screener.py
```

The script will:
1. Connect to FinViz with your configured filters
2. Scrape all pages of results
3. Export to `FinVizData.csv` with timestamp

### Configuration

Edit the `url` variable in `main()` to customize your screening criteria:

```python
url = "https://finviz.com/screener.ashx?v=121&f=cap_smallover,sh_relvol_o2,ta_perf_d5o&ft=4&o=-marketcap"
```

Current filters:
- Market cap: Small cap and above
- Relative volume: Over 2x
- Performance: Up 5%+ today
- Sorted by: Market cap (descending)

## Output

`FinVizData.csv` - CSV file containing:
- Ticker symbols
- Market cap, P/E ratios, valuations
- Growth metrics (EPS, Sales)
- Current price, change, volume
- Scraped timestamp

## Deployment

This is a production repository. Only deployment-ready code should be committed here.

Development and experimental work should be done in the `dev` directory.

## License

Personal project - All rights reserved
