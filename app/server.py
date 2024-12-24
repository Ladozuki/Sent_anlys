# server.py
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import json

# Initialize Flask app
app = Flask(__name__)

# Load configuration and model
with open("config/vessel_config.json", "r") as f:
    config = json.load(f)

model = joblib.load("models/model.joblib")

def preprocess_input(data):
    """Preprocess input data to match model requirements."""
    df = pd.DataFrame(data)
    df["Supply-Demand Gap"] = df["Demand Index"] - df["Supply Index"]
    numerical_features = ["Demand Index", 'Oil Price ($/barrel)', 'GDP Growth (%)', 'Weather Impact', 
                          "Supply Index", "Sentiment Score", "Supply-Demand Gap"]
    df = df[numerical_features]
    return df

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Parse incoming data
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided."}), 400

        # Preprocess and predict
        preprocessed_data = preprocess_input(data)
        predictions = model.predict(preprocessed_data)
        return jsonify({"predictions": predictions.tolist()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/voyage-insights", methods=["POST"])
def voyage_insights():
    try:
        # Extract parameters
        data = request.json
        required_fields = ["route", "vessel_type", "fuel_price", "base_rate"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {missing_fields}"}), 400

        route = data["route"]
        vessel_type = data["vessel_type"]
        fuel_price = data["fuel_price"]
        base_rate = data["base_rate"]
        seasonality = data.get("seasonality", 1.0)
        congestion = data.get("congestion", 1.0)
        weather = data.get("weather", 1.0)

        # Fetch route and vessel details
        if route not in config["routes"]:
            return jsonify({"error": f"Route {route} not found in configuration."}), 404
        if vessel_type not in config["vessel_types"]:
            return jsonify({"error": f"Vessel type {vessel_type} not found in configuration."}), 404

        route_data = config["routes"][route]
        vessel_data = config["vessel_types"][vessel_type]

        # Calculate insights
        distance_nm = route_data["distance_nm"]
        port_fees = route_data["port_fees"]
        canal_fees = route_data.get("canal_fees", 0)
        consumption_rate = vessel_data["daily_consumption"]
        speed_knots = vessel_data["average_speed_knots"]

        voyage_days = distance_nm / (speed_knots * 24)
        fuel_required = voyage_days * consumption_rate
        voyage_cost = port_fees + canal_fees + (fuel_required * fuel_price)

        adjusted_rate = base_rate * seasonality * congestion * weather

        # Compile results
        insights = {
            "voyage_days": voyage_days,
            "fuel_required_tons": fuel_required,
            "voyage_cost": voyage_cost,
            "adjusted_freight_rate": adjusted_rate,
            "sentiment_score": route_data.get("sentiment_score", 0),
            "seasonality_factor": seasonality,
            "congestion_factor": congestion,
            "weather_factor": weather
        }
        return jsonify(insights)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
