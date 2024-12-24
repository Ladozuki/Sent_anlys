# Project: Freight Rate Dashboard with Sentiment Analysis

## **Directory Structure Overview**

# Structure Recap
# - app/dash_app.py: Dash-based visualization and interactivity.
# - server.py: Flask server for API integration.
# - config/vessel_config.json: Configuration and static data for routes and vessel types.
# - models/models.py: Model training and evaluation.
# - utils/news_api.py: Sentiment data gathering and integration.
# - utils/pdf_gen.py: Automated PDF reporting module.

### Instructions for High-Quality Implementation


# app/dash_app.py
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os
import joblib
import json

# Load data and models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "../data/processed/df_gen.csv")
config_path = os.path.join(BASE_DIR, "../config/vessel_config.json")
model_path = os.path.join(BASE_DIR, "../models/model.joblib")

# Load data and configs
df = pd.read_csv(data_path)
with open(config_path, "r") as f:
    config = json.load(f)
model = joblib.load(model_path)

# Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Freight Rate Dashboard"

app.layout = dbc.Container([
    html.H1("Freight Rate Dashboard", className="text-center"),
    dcc.Tabs([
        dcc.Tab(label="Freight Rate Prediction", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Input Parameters"),
                        dbc.CardBody([
                            dbc.Label("Vessel Type"),
                            dcc.Dropdown(
                                id="vessel_type",
                                options=[{"label": t, "value": t} for t in df["Vessel Type"].unique()],
                                placeholder="Select vessel type"
                            ),
                            dbc.Label("Route ID"),
                            dcc.Dropdown(
                                id="route_id",
                                options=[{"label": r, "value": r} for r in df["Route ID"].unique()],
                                placeholder="Select route ID"
                            ),
                            dbc.Button("Predict", id="predict-btn", color="primary", className="mt-3")
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Prediction Results"),
                        dbc.CardBody([
                            html.Div(id="prediction-output", className="mt-3")
                        ])
                    ])
                ], width=8)
            ])
        ]),
        dcc.Tab(label="Trend Analysis", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Filter Options"),
                        dbc.CardBody([
                            dbc.Label("Feature"),
                            dcc.Dropdown(
                                id="feature",
                                options=[
                                    {"label": "Charter Price", "value": "Charter Price ($/day)"},
                                    {"label": "Sentiment Score", "value": "Sentiment Score"}
                                ],
                                placeholder="Select a feature"
                            )
                        ])
                    ])
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Trend Visualization"),
                        dbc.CardBody([
                            dcc.Graph(id="trend-graph")
                        ])
                    ])
                ], width=8)
            ])
        ])
    ])
], fluid=True)

@app.callback(
    Output("prediction-output", "children"),
    [Input("vessel_type", "value"), Input("route_id", "value"), Input("predict-btn", "n_clicks")]
)
def predict_freight_rate(vessel_type, route_id, n_clicks):
    if n_clicks is None or not vessel_type or not route_id:
        return "Please select all inputs and click Predict."

    route_config = config["routes"].get(route_id, {})
    demand_index = route_config.get("demand_index")
    supply_index = route_config.get("supply_index")
    sentiment_score = route_config.get("sentiment_score")

    input_df = pd.DataFrame([{ "Demand Index": demand_index, "Supply Index": supply_index, "Sentiment Score": sentiment_score }])
    predicted_rate = model.predict(input_df)[0]

    return f"Predicted Freight Rate: ${predicted_rate:.2f}"

@app.callback(
    Output("trend-graph", "figure"),
    [Input("feature", "value")]
)
def update_trend_graph(feature):
    fig = px.line(df, x="Charter Date", y=feature, color="Vessel Type")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
