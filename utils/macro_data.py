import sys
print(sys.path)


import sys
import os

import requests
from Sent_anlys.database.db_config import Session
from Sent_anlys.database.db_models import MacroData



def fetch_oil_prices(api_key):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=WTI&apikey={api_key}"
    session = Session()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("Monthly Time Series", {})
            for date, metrics in data.items():
                session.add(MacroData(date=date, metric="Oil Price", value=float(metrics["4. close"])))
            session.commit()
            print("Oil price data saved to database.")
        else:
            print(f"Error fetching oil prices: {response.status_code} - {response.text}")
    finally:
        session.close()

def fetch_gdp_growth(api_key):
    url = f"https://www.alphavantage.co/query?function=REAL_GDP&interval=quarterly&apikey={api_key}"
    session = Session()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("data", [])
            for record in data:
                session.add(MacroData(date=record["date"], metric="GDP Growth", value=float(record["value"])))
            session.commit()
            print("GDP growth data saved to database.")
        else:
            print(f"Error fetching GDP growth data: {response.status_code} - {response.text}")
    finally:
        session.close()

def fetch_trade_volumes(api_key):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=SPY&apikey={api_key}"
    session = Session()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("Monthly Time Series", {})
            for date, metrics in data.items():
                session.add(MacroData(date=date, metric="Trade Volume", value=float(metrics["5. volume"])))
            session.commit()
            print("Trade volume data saved to database.")
        else:
            print(f"Error fetching trade volume data: {response.status_code} - {response.text}")
    finally:
        session.close()

def fetch_inflation_rates(api_key):
    url = f"https://www.alphavantage.co/query?function=INFLATION&interval=monthly&apikey={api_key}"
    session = Session()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("data", [])
            for record in data:
                session.add(MacroData(date=record["date"], metric="Inflation Rate", value=float(record["value"])))
            session.commit()
            print("Inflation rate data saved to database.")
        else:
            print(f"Error fetching inflation rate data: {response.status_code} - {response.text}")
    finally:
        session.close()

def fetch_industrial_production(api_key):
    url = f"https://www.alphavantage.co/query?function=INDUSTRIAL_PRODUCTION&interval=monthly&apikey={api_key}"
    session = Session()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("data", [])
            for record in data:
                session.add(MacroData(date=record["date"], metric="Industrial Production", value=float(record["value"])))
            session.commit()
            print("Industrial production data saved to database.")
        else:
            print(f"Error fetching industrial production data: {response.status_code} - {response.text}")
    finally:
        session.close()

# Example usage
if __name__ == "__main__":
    API_KEY = "1UGCGOW5V20L24UB"
    fetch_oil_prices(API_KEY)
    fetch_gdp_growth(API_KEY)
    fetch_trade_volumes(API_KEY)
    fetch_inflation_rates(API_KEY)
    fetch_industrial_production(API_KEY)
