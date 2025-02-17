import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Concatenate, LSTM
from transformers import BertTokenizer, TFBertModel
from sklearn.preprocessing import StandardScaler
import joblib
import xgboost as xgb

freight_path = "/mnt/data/freight_rates.csv"
news_path = "/mnt/data/news_sentiment.csv"
market_path = "/mnt/data/maritime_data_2025.csv"

freight_df = pd.read_csv(r"C:\Users\User\Documents\Projects\Sent_anlys\freight_rates.csv")
news_df = pd.read_csv(r"C:\Users\User\Documents\Projects\Sent_anlys\news_sentiment.csv")
market_df = pd.read_csv(r"C:\Users\User\Documents\Projects\Sent_anlys\maritime_data_2025.csv")

# Ensure 'topic' is a string column and handle NaN values
news_df["topic"] = news_df["topic"].astype(str).fillna("")

# Extract clean route codes from topics
news_df["clean_topic"] = news_df["topic"].str.extract(r"@(\w+)")

# Handle cases where no match is found (avoid NaN issues)
news_df["clean_topic"].fillna("", inplace=True)

# Strip any whitespace (just in case)
news_df["clean_topic"] = news_df["clean_topic"].str.strip()

# Ensure 'Symbol' column exists in market_df
if "Symbol" not in market_df.columns:
    raise KeyError("The 'Symbol' column is missing in market_df!")

# Pivot market data so that each symbol has its own column
market_wide = market_df.pivot(index="Date", columns="Symbol", values="Close").ffill()

# Actual available symbols in dataset
symbols = [ 
    'FRO', 'GLNG', 'TK', 'CL=F', 'BZ=F', 'STNG', 'GC=F', 'SI=F', 
    'SHEL.L', 'BP', 'NMM', 'SBLK', 'GSL', 'DAC'
]

# Filter only symbols that actually exist in market_wide
available_symbols = [sym for sym in symbols if sym in market_wide.columns]

if not available_symbols:
    raise ValueError("None of the provided symbols exist in the market data.")

# Compute global market factors from the available symbols
global_market_factors = market_wide[available_symbols].mean().reset_index()

# Debugging step to check what symbols are actually being used
print("Using Symbols:", available_symbols)



# Prepare LSTM Inputs
sequence_length = 10
X_sequences = []
y_targets = []

for route in freight_df["Route"].unique():
    route_market = market_wide[available_symbols].values[-sequence_length:]  # Last 10 days
    route_sentiment = news_df[news_df["clean_topic"] == route]["sentiment_score"].values[-sequence_length:]

    # Fill missing sentiment with 0
    if len(route_sentiment) < sequence_length:
        route_sentiment = np.pad(route_sentiment, (sequence_length - len(route_sentiment), 0), 'constant', constant_values=0)

    X_sequences.append(np.hstack([route_market, route_sentiment.reshape(-1, 1)]))
    y_targets.append(freight_df[freight_df["Route"] == route]["Change (TCE)"].values[0])

X_sequences = np.array(X_sequences)
y_targets = np.array(y_targets)

# Define LSTM Model
lstm_input = Input(shape=(sequence_length, X_sequences.shape[2]))
lstm_out = LSTM(50, return_sequences=True)(lstm_input)
lstm_out = LSTM(25, return_sequences=False)(lstm_out)
lstm_model = tf.keras.Model(inputs=lstm_input, outputs=lstm_out)

# 🔹 BERT Model for Sentiment Analysis
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = TFBertModel.from_pretrained("bert-base-uncased")

tokens = tokenizer(news_df["description"].tolist(), padding=True, truncation=True, return_tensors="tf")
tokens_tf = {k: tf.convert_to_tensor(v) for k, v in tokens.items()}
bert_embeddings_np = bert_model(tokens_tf["input_ids"]).last_hidden_state[:, 0, :].numpy()  # Shape (N, 768)

# Convert BERT embeddings to DataFrame
X_sentiment = pd.DataFrame(bert_embeddings_np, columns=[f"bert_{i}" for i in range(bert_embeddings_np.shape[1])])
X_sentiment["clean_topic"] = news_df["clean_topic"]

# Group BERT embeddings by route (mean pooling per route)
X_sentiment_grouped = X_sentiment.groupby("clean_topic").mean().reset_index()

# Keep only routes present in freight_df
X_sentiment_grouped = X_sentiment_grouped[X_sentiment_grouped["clean_topic"].isin(freight_df["Route"])]

# Ensure all 20 routes are present in sentiment data
all_routes = freight_df["Route"].unique()
X_sentiment_grouped = X_sentiment_grouped.set_index("clean_topic").reindex(all_routes).fillna(0).reset_index()

# Ensure BERT embeddings match LSTM sequences
aligned_X_sentiment = X_sentiment_grouped.drop(columns=["clean_topic"]).values

# 🔹 **Reduce BERT Embeddings from 768 to 99**
bert_projector = Dense(99, activation="relu")  # Projection Layer
# Define BERT input layer
bert_input = Input(shape=(768,), name="bert_projected_input")  # Still expects 768

# Apply projection layer **inside the model**
bert_projected = Dense(99, activation="relu", name="bert_projection")(bert_input)  # 768 → 99

# Merge LSTM and projected BERT outputs
final_input = Concatenate()([lstm_model.output, bert_projected])

# Final output layer
final_output = Dense(1, activation="linear")(final_input)

# Define the Hybrid Model
hybrid_model = tf.keras.Model(inputs=[lstm_input, bert_input], outputs=final_output)

# Compile the model
hybrid_model.compile(optimizer="adam", loss="mse")

# Train Hybrid Model
hybrid_model.fit([X_sequences, aligned_X_sentiment], y_targets, epochs=20, batch_size=8)


# Save the trained model in Keras format
model_path = "models_saved/hybrid_freight_model.keras"
hybrid_model.save(model_path)
print(f"✅ Hybrid Model Saved: {model_path}")

