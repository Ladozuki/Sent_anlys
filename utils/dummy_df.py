import json
import pandas as pd
import os
import random
from datetime import date, timedelta

# Load configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "../config/vessel_config.json")
sentiment_data_path = os.path.join(BASE_DIR, "../sentiment_analysis.csv")
macro_data_path = os.path.join(BASE_DIR, "../macro_data.csv")
output_path = os.path.join(BASE_DIR, "../merged.csv")

# Load configurations
with open(config_path, "r") as f:
    config = json.load(f)

# Load real data
sentiment_df = pd.read_csv(sentiment_data_path)
macro_df = pd.read_csv(macro_data_path)

# Generate synthetic data
def random_value(range_tuple):
    return random.uniform(*range_tuple) if isinstance(range_tuple[0], float) else random.randint(*range_tuple)

def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# Combine real and synthetic data
def generate_data(samples, start_date, end_date):
    data = {
        "Charter Date": [],
        "Vessel Type": [],
        "Route ID": [],
        "Demand Index": [],
        "Supply Index": [],
        "Sentiment Score": [],  # From news data
        "Charter Price ($/day)": [],
        "Duration (days)": [],
        "Cargo Type/Use Case": [],
        "Daily Consumption": [],
        "Distance (nm)": [],
        "Port Fees ($)": [],
        "Average Speed (knots)": [],
        "Oil Price ($/barrel)": [],  # From macro data
        "GDP Growth (%)": [],  # From macro data
        "Supply-Demand Gap": [],
    }

    for _ in range(samples):
        route_id = random.choice(list(config["routes"].keys()))
        route_config = config["routes"][route_id]
        vessel_type = random.choice(route_config["frequent_vessels"])
        vessel_config = config["vessel_types"][vessel_type]

        average_speed = vessel_config.get("average_speed_knots", 1) or 1

        # Real data integrations
        sentiment_score = sentiment_df["sentiment_score"].sample().values[0]
        oil_price = macro_df["Oil Price ($/barrel)"].sample().values[0]
        gdp_growth = macro_df["GDP Growth (%)"].sample().values[0]

        # Generate synthetic data
        data["Charter Date"].append(random_date(start_date, end_date))
        data["Vessel Type"].append(vessel_type)
        data["Route ID"].append(route_id)
        data["Demand Index"].append(route_config.get("demand_index", random.randint(50, 100)))
        data["Supply Index"].append(route_config.get("supply_index", random.randint(50, 100)))
        data["Sentiment Score"].append(sentiment_score)
        data["Charter Price ($/day)"].append(random_value(vessel_config.get("charter_price_range", (5000, 10000))))
        data["Duration (days)"].append(route_config["distance_nm"] / average_speed / 24)
        data["Cargo Type/Use Case"].append(random.choice(vessel_config.get("cargo_types", ["Unknown"])))
        data["Daily Consumption"].append(vessel_config.get("daily_consumption", 0))
        data["Distance (nm)"].append(route_config["distance_nm"])
        data["Port Fees ($)"].append(route_config["port_fees"])
        data["Average Speed (knots)"].append(average_speed)
        data["Oil Price ($/barrel)"].append(oil_price)
        data["GDP Growth (%)"].append(gdp_growth)
        data["Supply-Demand Gap"].append(data["Demand Index"][-1] - data["Supply Index"][-1])

    return pd.DataFrame(data)

# Generate and save data
df = generate_data(samples=450, start_date=date(2024, 1, 1), end_date=date(2024, 12, 23))
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)
print(f"Data generated successfully! File saved to {output_path}")
