import os
import requests
import pandas as pd
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("macro_data_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MacroDataCollector")

class MacroDataCollector:
    """
    Collects macroeconomic data relevant to maritime shipping using Alpha Vantage API.
    Includes file-based storage for environments without database access.
    """
    def __init__(self, api_key, output_dir="data"):
        self.api_key = api_key
        self.output_dir = output_dir
        self.base_url = "https://www.alphavantage.co/query"
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "raw"), exist_ok=True)
        
    def fetch_data(self, function, metric, interval="weekly", limit=20):
        """
        Fetch data from Alpha Vantage API
        
        Args:
            function: Alpha Vantage function name
            metric: Name to save the data under
            interval: Data interval (weekly/monthly)
            limit: Maximum number of records to keep
            
        Returns:
            DataFrame with the fetched data or None if failed
        """
        params = {
            "function": function,
            "interval": interval,
            "apikey": self.api_key
        }
        
        try:
            logger.info(f"Fetching {metric} data...")
            response = requests.get(self.base_url, params=params)
            
            # Save raw response for debugging
            raw_path = os.path.join(self.output_dir, "raw", f"{metric.lower().replace(' ', '_')}_raw.json")
            with open(raw_path, 'w') as f:
                json.dump(response.json(), f, indent=2)
                
            if response.status_code == 200:
                data = response.json()
                
                # Handle different API response formats
                if "data" in data:
                    records = data["data"]
                elif "Weekly Time Series" in data:
                    # Handle time series format
                    ts_data = data["Weekly Time Series"]
                    records = [{"date": date, "value": float(values["4. close"])} 
                              for date, values in ts_data.items()]
                else:
                    logger.warning(f"Unexpected data format for {metric}")
                    return None
                
                if not records:
                    logger.warning(f"No data found for {metric}")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(records)
                
                # Limit records if specified
                if limit and len(df) > limit:
                    df = df.head(limit)
                
                # Add metadata
                df["metric"] = metric
                df["retrieved_date"] = datetime.now().strftime("%Y-%m-%d")
                
                return df
                
            else:
                logger.error(f"Error fetching {metric}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.exception(f"Error fetching {metric} data: {e}")
            return None
    
    def save_data(self, df, filename=None):
        """Save DataFrame to CSV"""
        if df is None or df.empty:
            logger.warning("No data to save")
            return None
            
        if filename is None:
            metric = df["metric"].iloc[0].lower().replace(" ", "_")
            filename = f"{metric}.csv"
            
        output_path = os.path.join(self.output_dir, filename)
        df.to_csv(output_path, index=False)
        logger.info(f"✅ Saved {len(df)} records to {output_path}")
        return output_path
    
    def load_data(self, filename):
        """Load data from CSV"""
        input_path = os.path.join(self.output_dir, filename)
        if os.path.exists(input_path):
            return pd.read_csv(input_path)
        else:
            logger.warning(f"File not found: {input_path}")
            return None
    
    def fetch_all_indicators(self):
        """Fetch all relevant economic indicators"""
        indicators = [
            {"function": "WTI", "metric": "Oil Price", "interval": "weekly"},
            {"function": "BRENT", "metric": "Brent Oil Price", "interval": "weekly"},
            {"function": "NATURAL_GAS", "metric": "Natural Gas", "interval": "weekly"},
            {"function": "COPPER", "metric": "Copper", "interval": "weekly"},
            {"function": "REAL_GDP", "metric": "US GDP", "interval": "quarterly"},
            {"function": "CPI", "metric": "US Inflation", "interval": "monthly"}
        ]
        
        results = {}
        combined_df = pd.DataFrame()
        
        for indicator in indicators:
            df = self.fetch_data(
                indicator["function"], 
                indicator["metric"], 
                indicator.get("interval", "weekly")
            )
            
            if df is not None:
                results[indicator["metric"]] = df
                self.save_data(df)
                
                # Append to combined DataFrame
                combined_df = pd.concat([combined_df, df])
        
        # Save combined indicators
        if not combined_df.empty:
            self.save_data(combined_df, "combined_indicators.csv")
            
        return results
    
    def create_correlation_matrix(self):
        """Create correlation matrix between economic indicators"""
        # Load combined indicators if it exists
        df = self.load_data("combined_indicators.csv")
        
        if df is None or df.empty:
            logger.warning("No data available for correlation analysis")
            return None
            
        # Pivot to wide format for correlation analysis
        pivot_df = df.pivot_table(index="date", columns="metric", values="value")
        
        # Calculate correlation matrix
        corr_matrix = pivot_df.corr()
        
        # Save correlation matrix
        corr_path = os.path.join(self.output_dir, "indicator_correlations.csv")
        corr_matrix.to_csv(corr_path)
        logger.info(f"✅ Correlation matrix saved to {corr_path}")
        
        return corr_matrix

# Example usage
if __name__ == "__main__":
    API_KEY = "1UGCGOW5V20L24UB"  # Replace with your actual API key
    
    collector = MacroDataCollector(API_KEY)
    indicators = collector.fetch_all_indicators()
    
    # Create correlation matrix
    corr_matrix = collector.create_correlation_matrix()
    
    if corr_matrix is not None:
        print("\nCorrelation Matrix:")
        print(corr_matrix)