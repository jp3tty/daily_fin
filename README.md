# Daily Stock Analysis Dashboard

Stock analysis pipeline and Streamlit visualization dashboard for candlestick pattern analysis.

🔗 **Live App:** [dailyfin-cxtubrf4ninvvdyty6nf5p.streamlit.app](https://dailyfin-cxtubrf4ninvvdyty6nf5p.streamlit.app/)

## 🎯 Purpose

This repository provides:
- Automated daily stock screening from FinViz
- Technical indicator calculations (RSI, momentum, engulfing patterns)
- Interactive Streamlit dashboard for visualization
- Data pipeline that generates CSV files for analysis

## 🚀 Quick Start

### Run Data Pipeline

```bash
# 1. Screen stocks from FinViz
python stock_screener.py

# 2. Pull 90 days of candle data
python pull_stock_candles.py

# 3. Calculate engulfing patterns
python engulfing_indicator.py

# 4. Calculate momentum indicators
python momentum_indicator.py
```

### Run Streamlit Dashboard Locally

```bash
streamlit run streamlit_indicator_app.py
```

## 📦 Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 📂 Project Structure

```
daily_fin/
├── streamlit_indicator_app.py   # Main Streamlit dashboard (deployed)
├── components/                   # Visualization components
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
├── requirements.txt             # Python dependencies
├── saved_data/                  # Generated CSV output
│   ├── FinVizData.csv
│   ├── stock_candles_90d.csv
│   ├── FinVizData_with_engulfing_patterns.csv
│   └── FinVizData_with_momentum_indicators.csv
└── README.md
```

## 🔄 Data Pipeline Workflow

```
stock_screener.py
      │
      └─► saved_data/FinVizData.csv
              │
              └─► pull_stock_candles.py
                      │
                      └─► saved_data/stock_candles_90d.csv
                              │
                              ├─► engulfing_indicator.py
                              │       └─► saved_data/FinVizData_with_engulfing_patterns.csv
                              │
                              └─► momentum_indicator.py
                                      └─► saved_data/FinVizData_with_momentum_indicators.csv
```

## 📊 Streamlit Dashboard

The deployed Streamlit app provides an interactive dashboard with:

- **Ticker Table** - Paginated, sortable, filterable table with AG-Grid
- **Candlestick Charts** - Interactive Plotly charts with:
  - Price candlesticks with SMA 20/50
  - RSI indicator with overbought/oversold zones
  - Momentum indicator
  - Bullish/bearish momentum markers

### Dashboard Data Flow

```
GitHub (jp3tty/daily_fin/saved_data/)
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
| `data/loaders.py` | Fetch CSVs from GitHub (public repo) |
| `data/transformers.py` | Merge engulfing + momentum data, clean columns |
| `utils/indicators.py` | RSI, momentum, trend calculations for charts |
| `components/charts.py` | Plotly candlestick chart with indicators |

## 📋 Stock Selection Criteria

Stocks are selected via FinViz screener with these filters:

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
Downloads 90 days of OHLCV data from yfinance for all screened tickers (plus monitored tickers: INTC, SB, AMAT, AAPL, ALMS, FSMD, HOPE).

### `engulfing_indicator.py`
Detects bullish and bearish engulfing candlestick patterns.

| Signal | Description |
|--------|-------------|
| `Bullish` | Bullish engulfing pattern detected |
| `Bearish` | Bearish engulfing pattern detected |
| `Neutral` | No engulfing pattern |

### `momentum_indicator.py`
Calculates momentum indicators and trend signals.

**Indicators:**
- RSI (14-period)
- Price Momentum (10-day)
- SMA 20 & SMA 50
- Momentum Strength %

**Trend Signals:**
| Signal | Criteria |
|--------|----------|
| `Bullish` | RSI > 50, price > SMA20 > SMA50, momentum > 0 |
| `Bearish` | RSI < 50, price < SMA20 < SMA50, momentum < 0 |
| `Neutral` | Mixed signals |

**Strength Signals:**
| Signal | Criteria |
|--------|----------|
| `Strong_Bullish` | RSI > 70 or momentum strength > 5% |
| `Strong_Bearish` | RSI < 30 or momentum strength < -5% |
| `Normal` | Within normal ranges |

## ☁️ Deployment

### Streamlit Cloud

The app is deployed on Streamlit Community Cloud:
- **Repository:** `jp3tty/daily_fin`
- **Main file:** `streamlit_indicator_app.py`
- **Data source:** CSV files from `saved_data/` in this repo (public)

### Updating the Dashboard

1. Run the data pipeline locally to generate new CSV files
2. Commit and push changes to GitHub
3. Streamlit Cloud automatically redeploys

```bash
git add saved_data/
git commit -m "Auto-update: Stock analysis $(date '+%Y-%m-%d %H:%M:%S')"
git push
```

## 🐛 Troubleshooting

### "Module not found" Error
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Streamlit AG-Grid Issues
```bash
pip install streamlit-aggrid
```

### Data Pipeline Failures
Run scripts in order — each depends on the previous output:
1. `stock_screener.py` (generates FinVizData.csv)
2. `pull_stock_candles.py` (reads FinVizData.csv)
3. `engulfing_indicator.py` (reads stock_candles_90d.csv)
4. `momentum_indicator.py` (reads stock_candles_90d.csv)

### Clear Streamlit Cache
If data isn't updating in the deployed app:
1. Go to the app → hamburger menu (top right) → "Clear cache"
2. Or reboot from Streamlit Cloud dashboard

---

**Last Updated:** 2025-12-17
