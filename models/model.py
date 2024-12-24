# models/models.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "../data/processed/df_gen.csv")
model_path = os.path.join(BASE_DIR, "../models/model.joblib")
scaler_path = os.path.join(BASE_DIR, "../models/scaler.pkl")

# Load Dataset
def load_data(data_path):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    df = pd.read_csv(data_path)
    return df

# Preprocess Data
def preprocess_data(df):
    # Feature Engineering
    df["Supply-Demand Gap"] = df["Demand Index"] - df["Supply Index"]

    # Numerical Columns to Scale
    numerical_features = [
        "Duration (days)", "Capacity/Bollard Pull", "Sentiment Score",
        "Oil Price ($/barrel)", "GDP Growth (%)", "Weather Impact", "Supply-Demand Gap"
    ]

    # One-hot Encode Categorical Columns
    df = pd.get_dummies(df, columns=["Vessel Type", "Cargo Type/Use Case", "Route ID"], drop_first=True)

    # Scale Numerical Features
    scaler = MinMaxScaler()
    df[numerical_features] = scaler.fit_transform(df[numerical_features])

    # Save Scaler
    joblib.dump(scaler, scaler_path)

    # Separate Features and Target
    X = df.drop(columns="Charter Price ($/day)", errors="ignore")
    y = df["Charter Price ($/day)"]

    return X, y

# Train Model
def train_model(X, y, model_path):
    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize Model
    model = RandomForestRegressor(random_state=42)

    # Train Model
    model.fit(X_train, y_train)

    # Evaluate Model
    y_pred = model.predict(X_test)
    print(f"MAE: {mean_absolute_error(y_test, y_pred)}")
    print(f"MSE: {mean_squared_error(y_test, y_pred)}")
    print(f"R2 Score: {r2_score(y_test, y_pred)}")

    # Save Model
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

# Main Execution
if __name__ == "__main__":
    try:
        # Load and Preprocess Data
        print("Loading data...")
        data = load_data(data_path)
        X, y = preprocess_data(data)

        # Train and Save Model
        print("Training model...")
        train_model(X, y, model_path)

    except Exception as e:
        print(f"Error: {e}")
