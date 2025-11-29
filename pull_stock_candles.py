import pandas as pd 
import yfinance as yf
from datetime import datetime, timedelta

# Configuration
DAYS_TO_PULL = 90

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
        
        print(f"📥 Batch downloading {len(symbol_list)} tickers (single API call)...")
        
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
            print(f"⚠️  No data returned")
            return None
            
        # Stack to convert from wide to long format
        # This moves the ticker symbols from columns to rows
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
        print(f"❌ Error downloading data: {str(e)}")
        return None


def main():
    """Main function to pull data for all tickers"""
    
    # Read ticker list from FinViz data
    print("Loading ticker list from FinVizData.csv...")
    try:
        df = pd.read_csv('saved_data/FinVizData.csv')
        symbol_list = df['Ticker'].tolist()
        print(f"✅ Found {len(symbol_list)} tickers to process\n")
    except FileNotFoundError:
        print("❌ Error: saved_data/FinVizData.csv not found!")
        return
    except Exception as e:
        print(f"❌ Error reading FinVizData.csv: {str(e)}")
        return
    
    # Pull data for all tickers in batch (avoids rate limiting!)
    print(f"{'='*60}")
    print(f"Pulling {DAYS_TO_PULL} days of stock data from yfinance...")
    print(f"{'='*60}\n")
    
    # Batch download - single API call for all tickers
    combined_df = pull_all_stock_data(symbol_list, days=DAYS_TO_PULL)
    
    # Save results
    if combined_df is not None and not combined_df.empty:
        print(f"\n{'='*60}")
        print("Saving to CSV...")
        print(f"{'='*60}\n")
        
        # Save to CSV
        output_file = 'saved_data/stock_candles_90d.csv'
        combined_df.to_csv(output_file, index=False)
        
        # Summary statistics
        print(f"✅ Data saved to '{output_file}'")
        print(f"\nSummary:")
        print(f"  Total Tickers Requested: {len(symbol_list)}")
        print(f"  Unique Tickers Retrieved: {combined_df['Ticker'].nunique()}")
        print(f"  Total Rows: {len(combined_df):,}")
        print(f"  Date Range: {combined_df['Date'].min()} to {combined_df['Date'].max()}")
        print(f"  File Size: {len(combined_df) * len(combined_df.columns)} data points")
        
        # Show sample
        print(f"\n{'='*60}")
        print("Sample Data (first 5 rows):")
        print(f"{'='*60}")
        print(combined_df.head().to_string(index=False))
        
        # Show tickers with most/least data points
        ticker_counts = combined_df['Ticker'].value_counts()
        print(f"\n{'='*60}")
        print("Data Coverage:")
        print(f"{'='*60}")
        print(f"  Max data points: {ticker_counts.max()} days ({ticker_counts.idxmax()})")
        print(f"  Min data points: {ticker_counts.min()} days ({ticker_counts.idxmin()})")
        print(f"  Average: {ticker_counts.mean():.1f} days per ticker")
        
    else:
        print("\n❌ No data was successfully retrieved!")
    
    print(f"\n{'='*60}")
    print("Process complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
