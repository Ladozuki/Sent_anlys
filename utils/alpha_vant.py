import requests
import pandas as pd
import os
import time

# Alpha Vantage API configuration
API_KEY = "1UGCGOW5V20L24UB"
BASE_URL = "https://www.alphavantage.co/query"

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(BASE_DIR, "../macro_data.csv")  # Save to root directory

# Fetch oil price data
# Fetch oil price data
def fetch_oil_prices():
    url = f"{BASE_URL}?function=TIME_SERIES_MONTHLY&symbol=WTI&apikey={API_KEY}"
    print(f"Fetching oil prices from {url}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            # Alpha Vantage uses "Monthly Time Series" for TIME_SERIES_MONTHLY
            monthly_prices = data.get("Monthly Time Series", {})
            if not monthly_prices:
                print("Oil price data is empty or malformed.")
                return pd.DataFrame()
            
            records = []
            for date, metrics in monthly_prices.items():
                records.append({
                    "Date": date,
                    "Oil Price ($/barrel)": float(metrics["4. close"])
                })
            print(f"Successfully fetched oil price data with {len(records)} records.")
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error parsing oil price data: {e}")
            return pd.DataFrame()
    else:
        print(f"Error fetching oil prices: {response.status_code} - {response.text}")
        return pd.DataFrame()


# Fetch GDP growth data
def fetch_gdp_growth():
    url = f"{BASE_URL}?function=REAL_GDP&interval=quarterly&apikey={API_KEY}"
    print(f"Fetching GDP growth data from {url}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            gdp_data = data.get("data", [])
            if not gdp_data:
                print("GDP growth data is empty or malformed.")
                return pd.DataFrame()
            
            records = []
            for record in gdp_data:
                records.append({
                    "Date": record["date"],
                    "GDP Growth (%)": float(record["value"])
                })
            print(f"Successfully fetched GDP growth data with {len(records)} records.")
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error parsing GDP growth data: {e}")
            return pd.DataFrame()
    else:
        print(f"Error fetching GDP growth data: {response.status_code} - {response.text}")
        return pd.DataFrame()

# Save macroeconomic data to CSV
def save_macro_data():
    # Fetch data
    print("Fetching oil prices...")
    oil_data = fetch_oil_prices()
    print("Fetching GDP growth data...")
    gdp_data = fetch_gdp_growth()

    # Merge datasets
    if not oil_data.empty and not gdp_data.empty:
        merged_data = pd.merge(oil_data, gdp_data, on="Date", how="outer").sort_values(by="Date")
    elif not oil_data.empty:
        merged_data = oil_data
    elif not gdp_data.empty:
        merged_data = gdp_data
    else:
        print("No data fetched. Exiting...")
        return

    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    merged_data.to_csv(output_path, index=False)
    print(f"Macro data saved to {output_path}")

if __name__ == "__main__":
    try:
        print("Starting macroeconomic data ingestion...")
        save_macro_data()
    except Exception as e:
        print(f"Error: {e}")
