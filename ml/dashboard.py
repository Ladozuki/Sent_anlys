import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define paths
DATA_DIR = "data"
RESULTS_DIR = "results"
MODELS_DIR = "models"

# Load data
def load_data():
    """Load all data needed for the dashboard"""
    data_package = {}
    
    # Load freight rates
    freight_path = os.path.join(DATA_DIR, "freight_rates.csv")
    if os.path.exists(freight_path):
        data_package["freight_df"] = pd.read_csv(freight_path)
    
    # Load market data
    market_path = os.path.join(DATA_DIR, "maritime_data_2025.csv")
    if os.path.exists(market_path):
        data_package["market_df"] = pd.read_csv(market_path)
    
    # Load ML predictions
    predictions_path = os.path.join(RESULTS_DIR, "route_predictions.csv")
    if os.path.exists(predictions_path):
        data_package["predictions_df"] = pd.read_csv(predictions_path)
    
    # Load model metrics
    metrics_path = os.path.join(MODELS_DIR, "training_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            data_package["model_metrics"] = json.load(f)
            
    # Load news sentiment data
    news_path = os.path.join(DATA_DIR, "news_sentiment.csv")
    if os.path.exists(news_path):
        data_package["news_df"] = pd.read_csv(news_path)
    
    return data_package

# Create summary metrics
def create_summary_metrics(data_package):
    """Create summary metrics for the dashboard"""
    summary = {}
    
    if "freight_df" in data_package and "Change (TCE)" in data_package["freight_df"].columns:
        freight_df = data_package["freight_df"]
        summary["avg_change"] = freight_df["Change (TCE)"].mean()
        summary["positive_routes"] = (freight_df["Change (TCE)"] > 0).sum()
        summary["negative_routes"] = (freight_df["Change (TCE)"] < 0).sum()
        summary["total_routes"] = len(freight_df)
        
    if "predictions_df" in data_package and "Predicted_Change" in data_package["predictions_df"].columns:
        predictions_df = data_package["predictions_df"]
        summary["avg_predicted_change"] = predictions_df["Predicted_Change"].mean()
        summary["positive_predictions"] = (predictions_df["Predicted_Change"] > 0).sum()
        summary["negative_predictions"] = (predictions_df["Predicted_Change"] < 0).sum()
        
    if "model_metrics" in data_package:
        metrics = data_package["model_metrics"]
        summary["model_mae"] = metrics.get("mae", 0)
        summary["model_rmse"] = metrics.get("rmse", 0)
        summary["model_r2"] = metrics.get("r2", 0)
        summary["training_date"] = metrics.get("training_date", datetime.now().strftime("%Y-%m-%d"))
        
    # Add sentiment metrics
    if "news_df" in data_package and "sentiment_score" in data_package["news_df"].columns:
        news_df = data_package["news_df"]
        summary["avg_sentiment"] = news_df["sentiment_score"].mean()
        summary["positive_news"] = (news_df["sentiment_score"] > 0.1).sum()
        summary["neutral_news"] = ((news_df["sentiment_score"] >= -0.1) & (news_df["sentiment_score"] <= 0.1)).sum()
        summary["negative_news"] = (news_df["sentiment_score"] < -0.1).sum()
        summary["total_news"] = len(news_df)
    
    return summary

# Create route-type classifications
def create_route_categories(data_package):
    """Categorize routes by type and region"""
    categories = {
        "west_africa": [],
        "middle_east": [],
        "black_sea": [],
        "americas": []
    }
    
    if "freight_df" in data_package:
        freight_df = data_package["freight_df"]
        
        for _, row in freight_df.iterrows():
            route = row["Route"]
            desc = row["Description"].lower() if "Description" in row else ""
            
            if "west africa" in desc:
                categories["west_africa"].append(route)
            elif "middle east" in desc or "kuwait" in desc:
                categories["middle_east"].append(route)
            elif "black sea" in desc:
                categories["black_sea"].append(route)
            elif "us gulf" in desc or "caribbean" in desc or "brazil" in desc:
                categories["americas"].append(route)
    
    return categories

# Generate word cloud
def generate_wordcloud_image(text, title="Word Cloud", width=800, height=400):
    """Generate word cloud image and return as base64 encoded string"""
    if not text or len(text) < 10:
        # Create a simple placeholder if text is insufficient
        wordcloud = WordCloud(width=width, height=height, background_color='white').generate("No sufficient text data")
    else:
        wordcloud = WordCloud(width=width, height=height, background_color='white').generate(text)
    
    plt.figure(figsize=(width/100, height/100))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title(title)
    plt.axis('off')
    
    # Save to a BytesIO object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format="png", bbox_inches='tight')
    plt.close()
    img_bytes.seek(0)
    
    # Encode to base64
    base64_image = base64.b64encode(img_bytes.read()).decode('utf-8')
    
    return base64_image

# Create figures
def create_figures(data_package):
    """Create plotly figures for the dashboard"""
    figures = {}
    
    # Only proceed if we have data
    if not data_package:
        return figures
    
    # 1. Current vs Predicted Change
    if "freight_df" in data_package and "predictions_df" in data_package:
        freight_df = data_package["freight_df"]
        predictions_df = data_package["predictions_df"]
        
        # Merge the data
        merged_df = pd.merge(
            freight_df, 
            predictions_df[["Route", "Predicted_Change", "Confidence"]], 
            on="Route", 
            how="left"
        )
        
        # Sort by current change
        merged_df = merged_df.sort_values("Change (TCE)", ascending=False)
        
        # Create figure
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=merged_df["Route"],
                y=merged_df["Change (TCE)"],
                name="Actual Change",
                marker_color="lightblue"
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Bar(
                x=merged_df["Route"],
                y=merged_df["Predicted_Change"],
                name="Predicted Change",
                marker_color="darkblue"
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=merged_df["Route"],
                y=merged_df["Confidence"],
                name="Prediction Confidence (%)",
                mode="markers",
                marker=dict(
                    size=10,
                    color="red",
                    symbol="diamond"
                )
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Current vs Predicted Rate Changes",
            xaxis_title="Route",
            yaxis_title="Change ($/day)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template="plotly_white",
            height=500
        )
        
        fig.update_yaxes(title_text="Confidence (%)", secondary_y=True)
        
        figures["current_vs_predicted"] = fig
    
    # 2. Route Type Analysis
    if "freight_df" in data_package:
        freight_df = data_package["freight_df"]
        
        # Separate dirty (TD) and clean (TC) routes
        dirty_routes = freight_df[freight_df["Route"].str.startswith("TD")]
        clean_routes = freight_df[freight_df["Route"].str.startswith("TC")]
        
        # Calculate average change
        dirty_avg = dirty_routes["Change (TCE)"].mean()
        clean_avg = clean_routes["Change (TCE)"].mean()
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=["Dirty Routes (TD)", "Clean Routes (TC)"],
                y=[dirty_avg, clean_avg],
                text=[f"{dirty_avg:.0f} $/day", f"{clean_avg:.0f} $/day"],
                textposition="auto",
                marker_color=["#1f77b4", "#ff7f0e"]
            )
        )
        
        fig.update_layout(
            title="Average Rate Change by Route Type",
            xaxis_title="Route Type",
            yaxis_title="Average Change ($/day)",
            template="plotly_white",
            height=400
        )
        
        figures["route_type_analysis"] = fig
    
    # 3. Route Performance Heatmap
    if "freight_df" in data_package and "predictions_df" in data_package:
        freight_df = data_package["freight_df"]
        predictions_df = data_package["predictions_df"]
        
        # Merge the data
        merged_df = pd.merge(
            freight_df, 
            predictions_df[["Route", "Predicted_Change", "Confidence"]], 
            on="Route", 
            how="left"
        )
        
        # Create a pivot table for the heatmap data
        pivot_data = []
        
        for _, row in merged_df.iterrows():
            current_change = row["Change (TCE)"]
            predicted_change = row["Predicted_Change"] if not pd.isna(row["Predicted_Change"]) else 0
            route = row["Route"]
            
            pivot_data.append({
                "Route": route,
                "Metric": "Current Change",
                "Value": current_change
            })
            
            pivot_data.append({
                "Route": route,
                "Metric": "Predicted Change",
                "Value": predicted_change
            })
        
        pivot_df = pd.DataFrame(pivot_data)
        
        # Create a pivot table
        heatmap_df = pivot_df.pivot(index="Route", columns="Metric", values="Value")
        
        # Sort by current change
        heatmap_df = heatmap_df.sort_values("Current Change", ascending=False)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_df.values,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            colorscale="RdBu",
            zmid=0,
            text=heatmap_df.values,
            texttemplate="%{text:.0f}",
            colorbar=dict(title="Change ($/day)")
        ))
        
        fig.update_layout(
            title="Current vs Predicted Change Heatmap",
            xaxis_title="Metric",
            yaxis_title="Route",
            template="plotly_white",
            height=800
        )
        
        figures["route_heatmap"] = fig
    
    # 4. Model Performance Graph
    if "model_metrics" in data_package:
        metrics = data_package["model_metrics"]
        
        # Extract metrics
        mae = metrics.get("mae", 0)
        rmse = metrics.get("rmse", 0)
        r2 = metrics.get("r2", 0)
        
        # Create gauges
        fig = make_subplots(
            rows=1, 
            cols=3,
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=mae,
                title={"text": "Mean Absolute Error ($/day)"},
                gauge={
                    "axis": {"range": [0, 3000]},
                    "bar": {"color": "orange"},
                    "steps": [
                        {"range": [0, 1000], "color": "lightgreen"},
                        {"range": [1000, 2000], "color": "lightyellow"},
                        {"range": [2000, 3000], "color": "lightcoral"}
                    ]
                }
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=rmse,
                title={"text": "Root Mean Square Error ($/day)"},
                gauge={
                    "axis": {"range": [0, 4000]},
                    "bar": {"color": "red"},
                    "steps": [
                        {"range": [0, 1000], "color": "lightgreen"},
                        {"range": [1000, 2500], "color": "lightyellow"},
                        {"range": [2500, 4000], "color": "lightcoral"}
                    ]
                }
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=r2,
                title={"text": "R² Score"},
                delta={"reference": 0, "increasing": {"color": "green"}},
                gauge={
                    "axis": {"range": [-1, 1]},
                    "bar": {"color": "blue"},
                    "steps": [
                        {"range": [-1, 0], "color": "lightcoral"},
                        {"range": [0, 0.5], "color": "lightyellow"},
                        {"range": [0.5, 1], "color": "lightgreen"}
                    ]
                }
            ),
            row=1, col=3
        )
        
        fig.update_layout(
            title="Model Performance Metrics",
            template="plotly_white",
            height=400
        )
        
        figures["model_performance"] = fig
        
    # 5. Sentiment Analysis by Route
    if "news_df" in data_package and "sentiment_score" in data_package["news_df"].columns and "clean_topic" in data_package["news_df"].columns:
        news_df = data_package["news_df"]
        
        # Group by route and calculate average sentiment
        route_sentiment = news_df.groupby("clean_topic")["sentiment_score"].agg(["mean", "count"]).reset_index()
        route_sentiment.columns = ["Route", "Avg_Sentiment", "Article_Count"]
        
        # Sort by average sentiment
        route_sentiment = route_sentiment.sort_values("Avg_Sentiment", ascending=False)
        
        # Create figure
        fig = go.Figure()
        
        # Add bar chart for average sentiment
        fig.add_trace(
            go.Bar(
                x=route_sentiment["Route"],
                y=route_sentiment["Avg_Sentiment"],
                name="Average Sentiment",
                marker_color=["green" if x > 0 else "red" for x in route_sentiment["Avg_Sentiment"]],
                text=route_sentiment["Avg_Sentiment"].round(2),
                textposition="auto"
            )
        )
        
        # Add scatter plot for article count
        fig.add_trace(
            go.Scatter(
                x=route_sentiment["Route"],
                y=route_sentiment["Article_Count"],
                name="Article Count",
                mode="markers",
                marker=dict(
                    size=route_sentiment["Article_Count"] * 2,
                    color="rgba(0, 0, 255, 0.6)",
                    line=dict(width=2)
                ),
                yaxis="y2"
            )
        )
        
        # Update layout
        fig.update_layout(
            title="News Sentiment Analysis by Route",
            xaxis_title="Route",
            yaxis=dict(
                title="Average Sentiment Score",
                side="left",
                range=[-1, 1]
            ),
            yaxis2=dict(
                title="Article Count",
                side="right",
                overlaying="y",
                range=[0, route_sentiment["Article_Count"].max() * 1.2]
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template="plotly_white",
            height=500
        )
        
        figures["sentiment_by_route"] = fig
        
    # 6. Sentiment vs Rate Change
    if ("news_df" in data_package and "sentiment_score" in data_package["news_df"].columns and 
        "freight_df" in data_package and "Change (TCE)" in data_package["freight_df"].columns):
        
        news_df = data_package["news_df"]
        freight_df = data_package["freight_df"]
        
        # Ensure we have clean_topic for joining
        if "clean_topic" in news_df.columns:
            # Group by route and calculate average sentiment
            route_sentiment = news_df.groupby("clean_topic")["sentiment_score"].mean().reset_index()
            route_sentiment.columns = ["Route", "Avg_Sentiment"]
            
            # Merge with freight data
            sentiment_vs_change = pd.merge(
                route_sentiment,
                freight_df[["Route", "Change (TCE)"]],
                on="Route",
                how="inner"
            )
            
            # Only proceed if we have matching routes
            if len(sentiment_vs_change) > 0:
                # Create figure
                fig = px.scatter(
                    sentiment_vs_change,
                    x="Avg_Sentiment",
                    y="Change (TCE)",
                    text="Route",
                    color="Change (TCE)",
                    color_continuous_scale="RdBu",
                    title="Sentiment Score vs Rate Change",
                    labels={
                        "Avg_Sentiment": "Average Sentiment Score",
                        "Change (TCE)": "Rate Change ($/day)"
                    },
                    height=500
                )
                
                # Update layout
                fig.update_traces(
                    textposition="top center",
                    marker=dict(size=12)
                )
                
                fig.update_layout(
                    xaxis=dict(
                        title="Average Sentiment Score",
                        range=[-1, 1]
                    ),
                    template="plotly_white"
                )
                
                figures["sentiment_vs_change"] = fig
        
    return figures

# Generate word clouds
def generate_word_clouds(data_package):
    """Generate word clouds for positive and negative sentiment"""
    word_clouds = {}
    
    if "news_df" in data_package and "sentiment_score" in data_package["news_df"].columns:
        news_df = data_package["news_df"]
        
        # Prepare text for positive sentiment
        positive_news = news_df[news_df["sentiment_score"] > 0.1]
        if len(positive_news) > 0:
            # Combine all relevant text fields
            positive_text = " ".join(
                positive_news["title"].fillna("") + " " + 
                positive_news["description"].fillna("")
            )
            word_clouds["positive"] = generate_wordcloud_image(
                positive_text, 
                title="Positive Sentiment Word Cloud"
            )
        
        # Prepare text for negative sentiment
        negative_news = news_df[news_df["sentiment_score"] < -0.1]
        if len(negative_news) > 0:
            # Combine all relevant text fields
            negative_text = " ".join(
                negative_news["title"].fillna("") + " " + 
                negative_news["description"].fillna("")
            )
            word_clouds["negative"] = generate_wordcloud_image(
                negative_text, 
                title="Negative Sentiment Word Cloud"
            )
    
    return word_clouds

# Build the dashboard layout
def build_layout(data_package, summary, figures, word_clouds):
    """Build the dashboard layout"""
    
    # Determine if we have route predictions
    has_predictions = "predictions_df" in data_package
    
    # Determine if we have model metrics
    has_metrics = "model_metrics" in data_package
    
    # Determine if we have news sentiment data
    has_sentiment = "news_df" in data_package
    
    # For demo purposes, we'll build a complete layout even if some data is missing
    
    layout = html.Div([
        # Header
        html.Div([
            html.H1("Maritime Analytics Dashboard", style={"textAlign": "center", "color": "#333"}),
            html.P(f"Last Updated: {datetime.now().strftime('%d %B %Y')}", style={"textAlign": "center", "fontStyle": "italic"})
        ]),
        
        # Executive Summary Section
        html.Div([
            html.H2("Executive Summary", style={"borderBottom": "1px solid #ddd", "paddingBottom": "10px"}),
            
            # Summary Cards Row
            html.Div([
                # Current Market Card
                html.Div([
                    html.H4("Current Market", style={"textAlign": "center", "color": "#333"}),
                    html.P([
                        "Average Change: ",
                        html.Span(
                            f"{summary.get('avg_change', 0):.2f} $/day", 
                            style={"color": "green" if summary.get('avg_change', 0) > 0 else "red", "fontWeight": "bold"}
                        )
                    ]),
                    html.P([
                        f"{summary.get('positive_routes', 0)} routes increasing, ",
                        f"{summary.get('negative_routes', 0)} routes decreasing"
                    ]),
                    html.P([
                        f"Total Routes: {summary.get('total_routes', 0)}"
                    ])
                ], className="summary-card"),
                
                # ML Predictions Card
                html.Div([
                    html.H4("ML Predictions", style={"textAlign": "center", "color": "#333"}),
                    html.P([
                        "Average Predicted Change: ",
                        html.Span(
                            f"{summary.get('avg_predicted_change', 0):.2f} $/day", 
                            style={"color": "green" if summary.get('avg_predicted_change', 0) > 0 else "red", "fontWeight": "bold"}
                        )
                    ]),
                    html.P([
                        f"{summary.get('positive_predictions', 0)} routes predicted to increase, ",
                        f"{summary.get('negative_predictions', 0)} routes predicted to decrease"
                    ]),
                    html.P([
                        f"Model Trained: {summary.get('training_date', 'Unknown')}"
                    ])
                ], className="summary-card"),
                
                # Sentiment Analysis Card
                html.Div([
                    html.H4("News Sentiment Analysis", style={"textAlign": "center", "color": "#333"}),
                    html.P([
                        "Average Sentiment: ",
                        html.Span(
                            f"{summary.get('avg_sentiment', 0):.2f}", 
                            style={"color": "green" if summary.get('avg_sentiment', 0) > 0 else "red", "fontWeight": "bold"}
                        )
                    ]),
                    html.P([
                        f"{summary.get('positive_news', 0)} positive, ",
                        f"{summary.get('neutral_news', 0)} neutral, ",
                        f"{summary.get('negative_news', 0)} negative articles"
                    ]),
                    html.P([
                        f"Total Articles: {summary.get('total_news', 0)}"
                    ])
                ], className="summary-card"),
                
                # Model Performance Card
                html.Div([
                    html.H4("Model Performance", style={"textAlign": "center", "color": "#333"}),
                    html.P([
                        "MAE: ",
                        html.Span(
                            f"{summary.get('model_mae', 0):.2f} $/day", 
                            style={"fontWeight": "bold"}
                        )
                    ]),
                    html.P([
                        "RMSE: ",
                        html.Span(
                            f"{summary.get('model_rmse', 0):.2f} $/day", 
                            style={"fontWeight": "bold"}
                        )
                    ]),
                    html.P([
                        "R² Score: ",
                        html.Span(
                            f"{summary.get('model_r2', 0):.2f}", 
                            style={"color": "green" if summary.get('model_r2', 0) > 0.5 else "red", "fontWeight": "bold"}
                        )
                    ])
                ], className="summary-card")
            ], style={"display": "flex", "justifyContent": "space-between", "margin": "20px 0"}),
            
            # ML Engine Status Alert
            html.Div([
                html.H4("ML Engine Status", style={"marginBottom": "10px"}),
                html.P([
                    "The ML Engine is currently in ", 
                    html.Strong("development phase"), 
                    ". The current R² score of ",
                    html.Strong(f"{summary.get('model_r2', 0):.2f}", style={"color": "red"}),
                    " indicates significant room for improvement in prediction accuracy."
                ]),
                html.P([
                    "Future enhancements will include: extended feature engineering, hyperparameter tuning, and incorporation of additional market data sources. ",
                    "The current model serves as a baseline for demonstrating the pipeline's capability."
                ])
            ], style={
                "padding": "15px", 
                "backgroundColor": "#f8f9fa", 
                "border": "1px solid #ddd", 
                "borderRadius": "5px",
                "marginBottom": "20px"
            })
        ]),
        
        # Tabs for different sections
        dcc.Tabs([
            # Rate Analysis Tab
            dcc.Tab(label="Rate Analysis", children=[
                html.Div([
                    html.H3("Current vs Predicted Rate Changes", style={"marginTop": "20px"}),
                    html.P("Compare actual rate changes with model predictions and confidence levels."),
                    dcc.Graph(
                        figure=figures.get("current_vs_predicted", {}) if has_predictions else go.Figure(),
                        config={"displayModeBar": True}
                    ),
                    
                    html.H3("Route Type Analysis", style={"marginTop": "20px"}),
                    html.P("Compare performance between dirty (TD) and clean (TC) routes."),
                    dcc.Graph(
                        figure=figures.get("route_type_analysis", {})
                    )
                ])
            ]),
            
            # Route Performance Tab
            dcc.Tab(label="Route Performance", children=[
                html.Div([
                    html.H3("Route Performance Heatmap", style={"marginTop": "20px"}),
                    html.P("Visualize current and predicted changes across all routes."),
                    dcc.Graph(
                        figure=figures.get("route_heatmap", {}) if has_predictions else go.Figure()
                    )
                ])
            ]),
            
            
            # Sentiment Analysis Tab
            dcc.Tab(label="Sentiment Analysis", children=[
                html.Div([
                    html.H3("News Sentiment by Route", style={"marginTop": "20px"}),
                    html.P("Average sentiment score and article count for each route."),
                    dcc.Graph(
                        figure=figures.get("sentiment_by_route", {}) if has_sentiment else go.Figure()
                    ),
                    
                    html.H3("Sentiment Score vs Rate Change", style={"marginTop": "20px"}),
                    html.P("Correlation between news sentiment and actual rate changes."),
                    dcc.Graph(
                        figure=figures.get("sentiment_vs_change", {}) if has_sentiment else go.Figure()
                    ),
                    
                    html.Div([
                        html.Div([
                            html.H3("Positive Sentiment Word Cloud", style={"textAlign": "center"}),
                            html.Img(
                                src=f"data:image/png;base64,{word_clouds.get('positive', '')}",
                                style={"width": "100%", "maxWidth": "600px", "margin": "0 auto", "display": "block"}
                            )
                        ], style={"flex": "1", "margin": "0 10px"}),
                        
                        html.Div([
                            html.H3("Negative Sentiment Word Cloud", style={"textAlign": "center"}),
                            html.Img(
                                src=f"data:image/png;base64,{word_clouds.get('negative', '')}",
                                style={"width": "100%", "maxWidth": "600px", "margin": "0 auto", "display": "block"}
                            )
                        ], style={"flex": "1", "margin": "0 10px"})
                    ], style={"display": "flex", "flexWrap": "wrap", "marginTop": "30px"}),
                    
                    html.H3("Top News Articles by Sentiment", style={"marginTop": "30px"}),
                    html.Div([
                        html.Div([
                            html.H4("Most Positive Articles", style={"textAlign": "center"}),
                            dash_table.DataTable(
                                data=(
                                    data_package.get("news_df", pd.DataFrame())
                                    .sort_values("sentiment_score", ascending=False)
                                    .head(5)
                                    [["title", "source", "sentiment_score", "clean_topic"]]
                                    .to_dict("records")
                                ) if has_sentiment else [],
                                columns=[
                                    {"name": "Title", "id": "title"},
                                    {"name": "Source", "id": "source"},
                                    {"name": "Sentiment", "id": "sentiment_score", "type": "numeric", "format": {"specifier": ".2f"}},
                                    {"name": "Route", "id": "clean_topic"}
                                ],
                                style_cell={"textAlign": "left", "padding": "8px"},
                                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                                style_data_conditional=[
                                    {"if": {"column_id": "sentiment_score"}, "color": "green", "fontWeight": "bold"}
                                ]
                            )
                        ], style={"flex": "1", "margin": "0 10px"}),
                        
                        html.Div([
                            html.H4("Most Negative Articles", style={"textAlign": "center"}),
                            dash_table.DataTable(
                                data=(
                                    data_package.get("news_df", pd.DataFrame())
                                    .sort_values("sentiment_score")
                                    .iloc[6:11]
                                    [["title", "source", "sentiment_score", "clean_topic"]]
                                    .to_dict("records")
                                ) if has_sentiment else [],
                                columns=[
                                    {"name": "Title", "id": "title"},
                                    {"name": "Source", "id": "source"},
                                    {"name": "Sentiment", "id": "sentiment_score", "type": "numeric", "format": {"specifier": ".2f"}},
                                    {"name": "Route", "id": "clean_topic"}
                                ],
                                style_table= {"overflowX": "auto"},
                                style_cell={"textAlign": "left", "padding": "8px",},
                                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                                style_data_conditional=[
                                    {"if": {"column_id": "sentiment_score"}, "color": "red", "fontWeight": "bold"}
                                ]
                            )
                        ], style={"flex": "1", "margin": "0 10px"})
                    ], style={"display": "flex", "flexWrap": "wrap"},)
                ])
            ]),
            
            # ML Performance Tab
            dcc.Tab(label="ML Performance", children=[
                html.Div([
                    html.H3("Model Performance Metrics", style={"marginTop": "20px"}),
                    html.P("Evaluate the ML model's prediction accuracy."),
                    dcc.Graph(
                        figure=figures.get("model_performance", {}) if has_metrics else go.Figure()
                    ),
                    
                    html.H3("Model Improvement Roadmap", style={"marginTop": "30px"}),
                    html.Div([
                        html.P("The current model shows areas for improvement, particularly in its R² score which indicates limited predictive power. Here's our roadmap for enhancing performance:"),
                        
                        html.H4("Short-term Improvements (Next Release):", style={"marginTop": "15px"}),
                        html.Ul([
                            html.Li("Feature Selection: Identify and remove features that add noise rather than signal"),
                            html.Li("Hyperparameter Tuning: Optimize model parameters using grid search"),
                            html.Li("Data Quality: Improve handling of outliers in training data")
                        ]),
                        
                        html.H4("Medium-term Enhancements:", style={"marginTop": "15px"}),
                        html.Ul([
                            html.Li("Advanced Feature Engineering: Develop route-specific features that capture market dynamics"),
                            html.Li("Ensemble Methods: Combine multiple models to improve prediction accuracy"),
                            html.Li("Historical Backtesting: Implement rigorous validation against historical data")
                        ]),
                        
                        html.H4("Long-term Vision:", style={"marginTop": "15px"}),
                        html.Ul([
                            html.Li("Deep Learning Integration: Implement LSTM/transformer models for time series forecasting"),
                            html.Li("Market Regime Detection: Automatically identify different market conditions"),
                            html.Li("Causal Analysis: Move beyond correlation to understand causal relationships")
                        ])
                    ], style={"backgroundColor": "#f8f9fa", "padding": "15px", "borderRadius": "5px"})
                ])
            ]),
            
            # Data Tables Tab
            dcc.Tab(label="Data Tables", children=[
                html.Div([
                    html.H3("Freight Rates", style={"marginTop": "20px"}),
                    dash_table.DataTable(
                        data=data_package.get("freight_df", pd.DataFrame()).to_dict("records"),
                        columns=[{"name": i, "id": i} for i in data_package.get("freight_df", pd.DataFrame()).columns],
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "textAlign": "left",
                            "padding": "8px",
                            "minWidth": "100px"
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold"
                        },
                        style_data_conditional=[
                            {
                                "if": {"column_id": "Change (TCE)", "filter_query": "{Change (TCE)} > 0"},
                                "color": "green"
                            },
                            {
                                "if": {"column_id": "Change (TCE)", "filter_query": "{Change (TCE)} < 0"},
                                "color": "red"
                            }
                        ],
                        page_size=10
                    ),
                    
                    html.H3("Route Predictions", style={"marginTop": "30px"}),
                    dash_table.DataTable(
                        data=data_package.get("predictions_df", pd.DataFrame()).to_dict("records"),
                        columns=[{"name": i, "id": i} for i in data_package.get("predictions_df", pd.DataFrame()).columns],
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "textAlign": "left",
                            "padding": "8px",
                            "minWidth": "100px"
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold"
                        },
                        style_data_conditional=[
                            {
                                "if": {"column_id": "Predicted_Change", "filter_query": "{Predicted_Change} > 0"},
                                "color": "green"
                            },
                            {
                                "if": {"column_id": "Predicted_Change", "filter_query": "{Predicted_Change} < 0"},
                                "color": "red"
                            }
                        ],
                        page_size=10
                    ),
                    
                    html.H3("News Sentiment", style={"marginTop": "30px"}),
                    dash_table.DataTable(
                        data=data_package.get("news_df", pd.DataFrame()).to_dict("records"),
                        columns=[{"name": i, "id": i} for i in data_package.get("news_df", pd.DataFrame()).columns],
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "textAlign": "left",
                            "padding": "8px",
                            "minWidth": "100px"
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold"
                        },
                        style_data_conditional=[
                            {
                                "if": {"column_id": "sentiment_score", "filter_query": "{sentiment_score} > 0"},
                                "color": "green"
                            },
                            {
                                "if": {"column_id": "sentiment_score", "filter_query": "{sentiment_score} < 0"},
                                "color": "red"
                            }
                        ],
                        page_size=10
                    )
                ])
            ])
        ])
    ], style={"maxWidth": "1200px", "margin": "0 auto", "padding": "20px"})
    
    return layout

# Load all data
data_package = load_data()

# Create summary metrics
summary = create_summary_metrics(data_package)

# Create route categories
categories = create_route_categories(data_package)

# Create figures
figures = create_figures(data_package)

# Generate word clouds
word_clouds = generate_word_clouds(data_package)

# Build the layout
app.layout = build_layout(data_package, summary, figures, word_clouds)

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Maritime Analytics Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                color: #333;
            }
            .summary-card {
                flex: 1;
                margin: 0 10px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .summary-card h4 {
                margin-top: 0;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }
            .tab-content {
                padding: 20px;
                background-color: white;
                border: 1px solid #ddd;
                border-top: none;
                border-radius: 0 0 5px 5px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Run the app
if __name__ == '__main__':
    app.run(debug=True)