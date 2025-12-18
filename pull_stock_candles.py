import pandas as pd 
import yfinance as yf
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
DAYS_TO_PULL = 90
ADDITIONAL_TICKERS = ['INTC', 'AMAT', 'AAPL', 'ALMS', 'FSMD', 'HOPE']

def pull_all_stock_data(symbol_list, days=90):
    """
    Download historical stock data for multiple tickers in batch (avoids rate limiting)
    
    Args:
        symbol_list: List of stock ticker symbols
        days: Number of days of historical data (default: 90)
        
    Returns:
        DataFrame with all ticker data in long format
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Download ALL tickers at once - this avoids rate limiting!
        df = yf.download(
            symbol_list, 
            start=start_date, 
            end=end_date, 
            progress=False, 
            auto_adjust=True,
            group_by='column'
        )
        
        if df.empty:
            logging.warning("No data returned from yfinance")
            return None
            
        # Stack to convert from wide to long format
        df = df.stack(level=1, future_stack=True).reset_index()
        df.rename(columns={'level_1': 'Ticker'}, inplace=True)

        # Standardize column names
        df.columns = [col.capitalize() if col.lower() != 'ticker' else 'Ticker'
                      for col in df.columns]

        # Reorder columns for clarity
        column_order = ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df[[col for col in column_order if col in df.columns]]

        return df
        
    except Exception as e:
        logging.error(f"Error downloading data: {str(e)}")
        return None


def main():
    """Main function to pull data for all tickers"""
    
    try:
        df = pd.read_csv('saved_data/FinVizData.csv')
        symbol_list = df['Ticker'].tolist()
        
        # Add monitored tickers
        symbol_list = list(set(symbol_list + ADDITIONAL_TICKERS))
        
        logging.info(f"Processing {len(symbol_list)} tickers")
        
    except FileNotFoundError:
        logging.error("saved_data/FinVizData.csv not found")
        return
    except Exception as e:
        logging.error(f"Error reading FinVizData.csv: {str(e)}")
        return
    
    # Batch download - single API call for all tickers
    combined_df = pull_all_stock_data(symbol_list, days=DAYS_TO_PULL)
    
    # Save results
    if combined_df is not None and not combined_df.empty:
        output_file = 'saved_data/stock_candles_90d.csv'
        combined_df.to_csv(output_file, index=False)
        logging.info(f"Saved {len(combined_df)} rows to {output_file}")
    else:
        logging.error("No data retrieved")


if __name__ == "__main__":
    main()
