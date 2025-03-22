import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("market_data_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MarketDataCollector")

class MarketDataCollector:
    """
    Collects market data for maritime-related stocks and commodities using yfinance.
    Includes robust error handling and rate limiting to avoid API issues.
    """
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Default symbols list
        self.default_symbols = [
            'FRO', 'GLNG', 'TK', 'CL=F', 'BZ=F', 'STNG', 'GC=F', 'SI=F', 
            'SHEL.L', 'BP', 'NMM', 'SBLK', 'GSL', 'DAC', 'GOGL', 'HO=F', 
            'BDRY', 'NAT'
        ]
        
        # Symbol categories for analysis
        self.symbol_categories = {
            'tanker': ['FRO', 'STNG', 'NAT', 'TK'],
            'lng': ['GLNG'],
            'drybulk': ['SBLK', 'GOGL', 'NMM'],
            'container': ['GSL', 'DAC'],
            'oil': ['CL=F', 'BZ=F', 'HO=F'],
            'metals': ['GC=F', 'SI=F'],
            'majors': ['SHEL.L', 'BP'],
            'index': ['BDRY']
        }

    def fetch_data_with_retry(self, symbols, start_date, end_date, max_retries=3):
        """Fetch data with retry logic to handle API limitations"""
        all_data = []
        
        for symbol in symbols:
            retries = 0
            success = False
            
            while retries < max_retries and not success:
                try:
                    logger.info(f"Fetching data for {symbol} ({retries+1}/{max_retries})")
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(start=start_date, end=end_date)
                    
                    if hist.empty:
                        logger.warning(f"No data returned for {symbol}")
                        retries += 1
                        time.sleep(1)  # Wait before retry
                        continue
                        
                    hist = hist[['Close']]
                    hist.reset_index(inplace=True)
                    hist['Symbol'] = symbol
                    
                    # Add symbol category
                    for category, syms in self.symbol_categories.items():
                        if symbol in syms:
                            hist['Category'] = category
                            break
                    else:
                        hist['Category'] = 'other'
                        
                    all_data.append(hist)
                    logger.info(f"✓ Successfully fetched data for {symbol}")
                    success = True
                    
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {str(e)}")
                    retries += 1
                    time.sleep(2)  # Wait longer after an error
            
            # Add a pause between symbols to avoid hitting rate limits
            time.sleep(0.5)
                
        return pd.concat(all_data) if all_data else pd.DataFrame()

    def fetch_multi_period_data(self, symbols=None):
        """Fetch data for multiple time periods"""
        if symbols is None:
            symbols = self.default_symbols
            
        today = datetime.now()
        
        # Define time periods
        periods = {
            'ytd': {
                'start': datetime(today.year, 1, 1),
                'end': today
            },
            'last_year': {
                'start': datetime(today.year-1, 1, 1),
                'end': datetime(today.year-1, 12, 31)
            },
            'year_before': {
                'start': datetime(today.year-2, 1, 1),
                'end': datetime(today.year-2, 12, 31)
            }
        }
        
        # Fetch data for each period
        all_period_data = {}
        for period_name, dates in periods.items():
            logger.info(f"Fetching {period_name} data ({dates['start']} to {dates['end']})...")
            period_data = self.fetch_data_with_retry(
                symbols, 
                dates['start'].strftime('%Y-%m-%d'),
                dates['end'].strftime('%Y-%m-%d')
            )
            
            if not period_data.empty:
                all_period_data[period_name] = period_data
            else:
                logger.warning(f"No data returned for {period_name}")
        
        return all_period_data
    
    def calculate_metrics(self, period_data):
        """Calculate various metrics from the collected data"""
        metrics = {}
        
        for period, data in period_data.items():
            # Calculate mean prices by symbol
            avg_prices = data.groupby('Symbol')['Close'].mean().round(2)
            metrics[f'{period}_avg'] = avg_prices
            
            # Calculate average by category
            category_avg = data.groupby('Category')['Close'].mean().round(2)
            metrics[f'{period}_category_avg'] = category_avg
            
        # Calculate YTD changes if we have both current and previous year data
        if 'ytd' in period_data and 'last_year' in period_data:
            ytd = period_data['ytd']
            last_year = period_data['last_year']
            
            # Get the latest prices for each symbol in YTD
            latest_prices = ytd.groupby('Symbol')['Close'].last()
            
            # Get the average prices from last year
            last_year_avg = last_year.groupby('Symbol')['Close'].mean()
            
            # Calculate percent change
            symbols_in_both = set(latest_prices.index) & set(last_year_avg.index)
            
            pct_changes = {}
            for symbol in symbols_in_both:
                pct_changes[symbol] = ((latest_prices[symbol] / last_year_avg[symbol]) - 1) * 100
                
            metrics['ytd_vs_lastyear_pct'] = pd.Series(pct_changes)
            
        return metrics
    
    def prepare_final_dataset(self, period_data, metrics):
        """Combine all data into a finalized dataset for analysis"""
        # Start with the latest data
        if 'ytd' in period_data and not period_data['ytd'].empty:
            final_data = period_data['ytd'].copy()
        else:
            logger.error("No YTD data available")
            return pd.DataFrame()
            
        # Add metadata columns
        final_data['DataCollectionDate'] = datetime.now().strftime('%Y-%m-%d')
        
        # Merge metrics
        for metric_name, metric_data in metrics.items():
            if isinstance(metric_data, pd.Series) and metric_name.endswith('_avg'):
                # Create a mapping dictionary from the Series
                avg_dict = metric_data.to_dict()
                
                # Apply the mapping to create new columns
                final_data[metric_name] = final_data['Symbol'].map(avg_dict)
        
        # Add YTD change column if available
        if 'ytd_vs_lastyear_pct' in metrics:
            change_dict = metrics['ytd_vs_lastyear_pct'].to_dict()
            final_data['YTD_Change_Pct'] = final_data['Symbol'].map(change_dict)
            
        return final_data
    
    def save_data(self, data, filename="maritime_data_2025.csv"):
        """Save the final dataset to CSV"""
        output_path = os.path.join(self.output_dir, filename)
        data.to_csv(output_path, index=False)
        logger.info(f"✅ Market data saved to: {output_path}")
        return output_path
    
    def run_collection(self):
        """Run the full data collection process"""
        logger.info("Starting market data collection...")
        
        # Fetch multi-period data
        period_data = self.fetch_multi_period_data()
        
        if all(df.empty for df in period_data.values()):
            logger.error("Failed to collect any market data")
            return None
            
        # Calculate metrics
        metrics = self.calculate_metrics(period_data)
        
        # Prepare final dataset
        final_data = self.prepare_final_dataset(period_data, metrics)
        
        # Save data
        if not final_data.empty:
            output_path = self.save_data(final_data)
            return output_path
        else:
            logger.error("Failed to prepare final dataset")
            return None

# Example usage
if __name__ == "__main__":
    collector = MarketDataCollector()
    output_path = collector.run_collection()
    
    if output_path:
        logger.info(f"Market data collection completed successfully. Data saved to {output_path}")
    else:
        logger.error("Market data collection failed")