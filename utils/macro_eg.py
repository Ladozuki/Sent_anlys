import sys
import os
import requests
from sqlalchemy import func
from Sent_anlys.database.db_config import Session
from Sent_anlys.database.db_models import MacroData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Uniform Fetch Function
def fetch_data(api_key, function, metric, interval="weekly", limit=None):
    """
    Fetch data from Alpha Vantage API and save to database.
    Parameters:
        - api_key: API key for Alpha Vantage.
        - function: The Alpha Vantage function (e.g., WTI, NATURAL_GAS).
        - metric: Metric name to save in the database.
        - interval: Data interval (e.g., 'weekly', 'monthly').
        - limit: Max records to fetch.
    """
    url = f"https://www.alphavantage.co/query"
    params = {"function": function, "interval": interval, "apikey": api_key}
    session = Session()

    try:
        logger.info(f"Fetching {metric} data...")
        response = requests.get(url, params=params)
        if response.status_code == 200:
            full_data = response.json()
            data = full_data.get("data", [])
            
            if not data:
                logger.warning(f"No data found for {metric}.")
                return
            
            # Process data and save records, with optional limit
            parsed_data = []
            for record in data:
                date = record.get("date")
                value = record.get("value")
                
                if date and value:
                    # Avoid duplicates by checking the database
                    existing_entry = (
                        session.query(MacroData)
                        .filter_by(date=date, metric=metric)
                        .first()
                    )
                    if not existing_entry:
                        session.add(MacroData(date=date, metric=metric, value=float(value)))
                        parsed_data.append({"date": date, "value": value})
                    
                    if limit and len(parsed_data) >= limit:
                        break
            
            session.commit()
            logger.info(f"Saved {len(parsed_data)} records for {metric}.")
        else:
            logger.error(f"Error fetching {metric}: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception(f"Error fetching {metric} data: {e}")
    finally:
        session.close()

# Example: Fetching Weekly Data
def fetch_oil_prices(api_key):
    fetch_data(api_key, "WTI", "Oil Price", interval="weekly", limit=20)

def fetch_natgas(api_key):
    fetch_data(api_key, "NATURAL_GAS", "Natural Gas", interval="weekly", limit=20)

def fetch_inflation_rates(api_key):
    fetch_data(api_key, "INFLATION", "Inflation Rate", interval="monthly", limit=20)

def fetch_industrial_production(api_key):
    fetch_data(api_key, "INDUSTRIAL_PRODUCTION", "Industrial Production", interval="monthly", limit=20)

# Example usage
if __name__ == "__main__":
    API_KEY = "1UGCGOW5V20L24UB"
    fetch_oil_prices(API_KEY)
    fetch_natgas(API_KEY)
    fetch_inflation_rates(API_KEY)
    fetch_industrial_production(API_KEY)
