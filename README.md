# Development Directory

Development and testing environment for stock analysis tools and Streamlit dashboard.

## 🎯 Purpose

This directory is for:
- Developing and testing new features
- Experimenting with analysis parameters
- Running local analysis before deploying to production
- Testing modifications to indicators and screeners
- Building and testing the Streamlit dashboard locally

## 🚀 Quick Start

### Run Analysis Pipeline

```bash
cd /Users/jeremypetty/Documents/projects/Financials/dev
./run_analysis.sh
```

### Run Streamlit Dashboard

```bash
cd /Users/jeremypetty/Documents/projects/Financials/dev
streamlit run streamlit_indicator_app.py
```

## 📦 Installation

### First Time Setup

```bash
# Navigate to project root
cd /Users/jeremypetty/Documents/projects/Financials

# Create virtual environment (if not already exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r dev/requirements.txt
```

### Streamlit Secrets Setup

Create `.streamlit/secrets.toml` for GitHub API access:

```bash
mkdir -p .streamlit
echo 'github_token = "your_github_token_here"' > .streamlit/secrets.toml
```

> **Note:** The `.streamlit/` folder should be in `.gitignore` to protect your token.

## 📂 Project Structure

```
dev/
├── streamlit_indicator_app.py   # Main Streamlit dashboard
├── components/                   # Streamlit visualization components
│   ├── __init__.py
│   └── charts.py                # Candlestick & momentum charts
├── data/                         # Data loading & transformation
│   ├── __init__.py
│   ├── loaders.py               # GitHub data fetching
│   └── transformers.py          # DataFrame merging & cleaning
├── utils/                        # Shared utilities
│   ├── __init__.py
│   └── indicators.py            # RSI, momentum calculations
├── stock_screener.py            # FinViz web scraper
├── pull_stock_candles.py        # yfinance data downloader
├── engulfing_indicator.py       # Engulfing pattern detection
├── momentum_indicator.py        # Momentum indicator analysis
├── run_analysis.sh              # Bash workflow runner
├── run_analysis.py              # Python workflow runner
├── requirements.txt             # Python dependencies
├── saved_data/                  # Generated CSV output
│   ├── FinVizData.csv
│   ├── stock_candles_90d.csv
│   ├── FinVizData_with_engulfing_patterns.csv
│   └── FinVizData_with_momentum_indicators.csv
└── .streamlit/
    └── secrets.toml             # GitHub token (not tracked in git)
```

## 🔄 Data Pipeline Workflow

```
run_analysis.sh
      │
      ├─► stock_screener.py
      │   └─► saved_data/FinVizData.csv
      │
      ├─► pull_stock_candles.py
      │   └─► saved_data/stock_candles_90d.csv
      │
      ├─► engulfing_indicator.py
      │   └─► saved_data/FinVizData_with_engulfing_patterns.csv
      │
      └─► momentum_indicator.py
          └─► saved_data/FinVizData_with_momentum_indicators.csv
```

## 📊 Streamlit Dashboard

The Streamlit app (`streamlit_indicator_app.py`) provides an interactive dashboard with:

- **Ticker Table** - Paginated, sortable, filterable table with AG-Grid
- **Candlestick Charts** - Interactive Plotly charts with:
  - Price candlesticks with SMA 20/50
  - RSI indicator with overbought/oversold zones
  - Momentum indicator
  - Bullish/bearish momentum markers

### Data Flow

```
GitHub (jp3tty/daily_fin)
      │
      └─► data/loaders.py (load_data_from_github)
          ├── FinVizData_with_momentum_indicators.csv
          ├── FinVizData_with_engulfing_patterns.csv
          └── stock_candles_90d.csv
                │
                └─► data/transformers.py (create_merged_df)
                    │
                    └─► Streamlit Display
                        ├── AG-Grid Table
                        └── Plotly Charts (components/charts.py)
```

### Modular Architecture

| Module | Purpose |
|--------|---------|
| `data/loaders.py` | Fetch CSVs from GitHub with authentication |
| `data/transformers.py` | Merge engulfing + momentum data, clean columns |
| `utils/indicators.py` | RSI, momentum, trend calculations for charts |
| `components/charts.py` | Plotly candlestick chart with indicators |

## 📋 Stock Selection Criteria

Stocks in the dashboard are selected via FinViz screener with these filters:

| Filter | Criteria |
|--------|----------|
| Market Cap | Small cap and above |
| Relative Volume | Over 2x average |
| 5-Day Performance | Over 5% gain |
| Sort | Market cap (descending) |

## 🔧 Analysis Scripts

### `stock_screener.py`
Scrapes FinViz for stocks matching the screening criteria.

### `pull_stock_candles.py`
Downloads 90 days of OHLCV data from yfinance for all screened tickers.

### `engulfing_indicator.py`
Detects bullish and bearish engulfing candlestick patterns.

**Signals:**
- `Bullish` - Bullish engulfing pattern detected
- `Bearish` - Bearish engulfing pattern detected
- `Neutral` - No engulfing pattern

### `momentum_indicator.py`
Calculates momentum indicators and trend signals.

**Indicators:**
- RSI (14-period)
- Price Momentum (10-day)
- SMA 20 & SMA 50
- Momentum Strength %

**Trend Signals:**
- `Bullish` - RSI > 50, price > SMA20 > SMA50, momentum > 0
- `Bearish` - RSI < 50, price < SMA20 < SMA50, momentum < 0
- `Neutral` - Mixed signals

**Strength Signals:**
- `Strong_Bullish` - RSI > 70 or momentum strength > 5%
- `Strong_Bearish` - RSI < 30 or momentum strength < -5%
- `Normal` - Within normal ranges

## 💡 Usage Tips

### Run Individual Scripts

```bash
# Re-run just the screener
python3 stock_screener.py

# Re-run just engulfing analysis
python3 engulfing_indicator.py

# Re-run just momentum analysis
python3 momentum_indicator.py
```

### Check Output Files

```bash
ls -lh saved_data/
head saved_data/FinVizData.csv
```

### Clear Streamlit Cache

If data isn't updating in Streamlit:
1. Click hamburger menu (top right) → "Clear cache"
2. Or restart: `Ctrl+C` then `streamlit run streamlit_indicator_app.py`

## 🐛 Troubleshooting

### "Module not found" Error

```bash
source ../.venv/bin/activate
pip install -r requirements.txt
```

### "GitHub token not found" Error

Create `.streamlit/secrets.toml`:
```bash
mkdir -p .streamlit
echo 'github_token = "ghp_your_token_here"' > .streamlit/secrets.toml
```

### Streamlit AG-Grid Issues

```bash
pip install streamlit-aggrid
```

### Script Fails with NameError

Ensure scripts are run in order (screener → candles → indicators), or use:
```bash
./run_analysis.sh
```

## 🧪 Development vs Production

| Aspect | Development (`dev/`) | Production (`prod/daily_fin/`) |
|--------|---------------------|-------------------------------|
| Purpose | Testing & experimentation | Stable, automated runs |
| Scheduling | Manual | GitHub Actions (daily 4:30 PM EST) |
| Output | Local only | Committed to repository |
| Streamlit | Local development | Streamlit Cloud (future) |

## 📝 Deployment Checklist

Before copying changes to production:

1. ✅ Test complete workflow: `./run_analysis.sh`
2. ✅ Verify all CSV files generated correctly
3. ✅ Check Streamlit dashboard displays data
4. ✅ Review summary statistics output
5. ✅ Copy updated scripts to `prod/daily_fin/`

---

**Development Environment**  
**Last Updated:** 2025-12-08
