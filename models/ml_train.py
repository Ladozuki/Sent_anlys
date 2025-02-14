import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
import numpy as np

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load data from CSV
csv_file_path = r"C:\Users\User\Documents\Projects\Sent_anlys\news_sentiment.csv"
freight_file_path = r"C:\Users\User\Documents\Projects\Sent_anlys\maritimepw\freight_rates.csv"


def prepare_data():
    """Fetch and merge sentiment & freight data"""
    news_df = pd.read_csv(csv_file_path)
    freight_df = pd.read_csv(freight_file_path)

    print("Columns in freight_df:", freight_df.columns)
    print("Columns in news_df:", news_df.columns)

    # Merge sentiment and freight data
    merged_df = pd.merge(freight_df, news_df, left_on="Route", right_on="topic", how="left")

    # Fill missing values
    merged_df["sentiment_score"].fillna(0, inplace=True)

    # Select features and target
    X = merged_df[["sentiment_score", "TCE", "OPEX"]]
    y = merged_df["Change (TCE)"]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

print("Data prepared for MLP model.")



# Import prepared data
X_train_scaled, X_test_scaled, y_train, y_test, scaler = prepare_data()

# Define MLP Model
model = keras.Sequential([
    keras.layers.Dense(64, activation="relu", input_shape=(X_train_scaled.shape[1],)),
    keras.layers.Dense(32, activation="relu"),
    keras.layers.Dense(1)  # Output layer for regression
])

# Compile model
model.compile(optimizer="adam", loss="mean_squared_error")

# Train model
model.fit(X_train_scaled, y_train, epochs=30, batch_size=8, verbose=1)

# Save model & scaler
model.save("models/mlp_freight_model.h5")
np.save("models/scaler.npy", scaler.mean_)

print("Neural Network Model Trained and Saved.")
