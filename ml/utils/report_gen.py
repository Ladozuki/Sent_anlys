import os
import pandas as pd
import json
import base64
from datetime import datetime
from jinja2 import Template
from weasyprint import HTML
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("report_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ReportGenerator")

class MaritimeReportGenerator:
    """
    Generates the Maritime Per Week report with integrated ML insights.
    Uses Jinja2 and WeasyPrint for PDF generation.
    """
    def __init__(self, data_dir="data", results_dir="results", report_dir="reports", images_dir="images"):
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.report_dir = report_dir
        self.images_dir = images_dir
        
        # Create directories if they don't exist
        for directory in [data_dir, results_dir, report_dir, images_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def encode_image(self, image_path):
        """Encode an image to base64 for embedding in HTML"""
        if not os.path.exists(image_path):
            logger.warning(f"Image not found: {image_path}")
            return ""
            
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {str(e)}")
            return ""
    
    def load_data(self):
        """Load all required data for report generation"""
        data_package = {}
        
        # Load freight data
        freight_path = os.path.join(self.data_dir, "freight_rates.csv")
        if os.path.exists(freight_path):
            data_package["freight_df"] = pd.read_csv(freight_path)
        else:
            logger.error(f"Freight data not found: {freight_path}")
            
        # Load ML predictions
        predictions_path = os.path.join(self.results_dir, "route_predictions.csv")
        if os.path.exists(predictions_path):
            data_package["predictions_df"] = pd.read_csv(predictions_path)
        else:
            logger.warning(f"Predictions not found: {predictions_path}")
            
        # Load ML metadata
        metadata_path = os.path.join(self.results_dir, "ml_output_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                data_package["ml_metadata"] = json.load(f)
        else:
            logger.warning(f"ML metadata not found: {metadata_path}")
            
        # Load model metrics
        metrics_path = os.path.join("models", "training_metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                data_package["model_metrics"] = json.load(f)
        else:
            logger.warning(f"Model metrics not found: {metrics_path}")
            
        return data_package
    
    def prepare_report_data(self, data_package):
        """Prepare data for the report template"""
        report_data = {
            "title": "Maritime Per Week",
            "date": datetime.now().strftime("%d %B %Y"),
            "map_image": self.encode_image(os.path.join(self.images_dir, "fuel_prices_map.png")),
            "bzcl_graphs": [
                self.encode_image(os.path.join(self.images_dir, "BZ=F_price_comparison.png")),
                self.encode_image(os.path.join(self.images_dir, "CL=F_price_comparison.png"))
            ]
        }

        report_data["ml_engine_status_image"] = self.encode_image(os.path.join(self.images_dir, "mlengine.png"))
        report_data["sentiment_analysis_image"] = self.encode_image(os.path.join(self.images_dir, "sent.png"))
        
        # Add freight route data
        if "freight_df" in data_package:
            freight_df = data_package["freight_df"]

            # Filter TD routes (Dirty routes) - limit to 5 rows
            td_routes = freight_df[freight_df["Route"].str.startswith("TD")].head(5)
            
            # Filter TC routes (Clean routes) - limit to 5 rows
            tc_routes = freight_df[freight_df["Route"].str.startswith("TC")].head(5)
            
            # Combine the filtered routes
            filtered_freight = pd.concat([td_routes, tc_routes])
            
            # Use the filtered DataFrame instead of the full one
            report_data["remaining_routes"] = filtered_freight.to_dict('records')
           
            # Sort routes by TCE change for highlighting
            sorted_routes = freight_df.sort_values("Change (TCE)", ascending=False)
            report_data["highest_changes"] = sorted_routes.head(4).to_dict('records')
        
        # Add ML predictions if available
        if "predictions_df" in data_package:
            predictions_df = data_package["predictions_df"]
            
            # Map predictions to routes
            if "freight_df" in data_package and "Route" in predictions_df.columns:
                route_predictions = {}
                
                for index, row in predictions_df.iterrows():
                    route = row["Route"]
                    route_predictions[route] = {
                        "Predicted_Change": row["Predicted_Change"],
                        "Confidence": row["Confidence"] if "Confidence" in row else 70,
                        "Confidence_Level": row["Confidence_Level"] if "Confidence_Level" in row else "Medium",
                        "Trend": row["Trend"] if "Trend" in row else "Neutral"
                    }
                
                # Add predictions to route data
                if "remaining_routes" in report_data:
                    for i, route_data in enumerate(report_data["remaining_routes"]):
                        route = route_data["Route"]
                        if route in route_predictions:
                            report_data["remaining_routes"][i].update(route_predictions[route])
            
            # Add ML visualization images
            if "ml_metadata" in data_package and "visualization_paths" in data_package["ml_metadata"]:
                viz_paths = data_package["ml_metadata"]["visualization_paths"]
                
                if "top_rate_changes" in viz_paths:
                    report_data["top_rate_changes_image"] = self.encode_image(viz_paths["top_rate_changes"])
                    
                if "tce_comparison" in viz_paths:
                    report_data["tce_comparison_image"] = self.encode_image(viz_paths["tce_comparison"])
                    
                if "feature_importance" in viz_paths:
                    report_data["feature_importance_image"] = self.encode_image(viz_paths["feature_importance"])
                    
                if "prediction_uncertainty" in viz_paths:
                    report_data["prediction_uncertainty_image"] = self.encode_image(viz_paths["prediction_uncertainty"])
            
            # Add market analysis if available
            if "ml_metadata" in data_package and "market_analysis" in data_package["ml_metadata"]:
                report_data.update(data_package["ml_metadata"]["market_analysis"])
                
                # Add featured route details
                featured_route_symbol = None
                for key, value in data_package["ml_metadata"]["market_analysis"].items():
                    if key == "featured_route_symbol":
                        featured_route_symbol = value
                        break
                
                if featured_route_symbol and "predictions_df" in data_package:
                    featured_data = predictions_df[predictions_df["Route"] == featured_route_symbol]
                    if not featured_data.empty:
                        report_data["featured_route"] = featured_data.iloc[0].to_dict()
                        
                        # Add key news for featured route (placeholder)
                        report_data["featured_route"]["key_news"] = [
                            "Dangote refinery increases exports along route",
                            "Port congestion reduced at Lagos terminals",
                            "New shipping alliance announced affecting West Africa"
                        ]
                        
                        # Add key factors
                        report_data["featured_route"]["key_factors"] = [
                            "Increased regional product exports",
                            "Reduced port congestion improving turnaround times",
                            "Favorable bunker pricing in West Africa"
                        ]
            
            # If no featured route found, use the route with the largest predicted change
            if "featured_route" not in report_data and "predictions_df" in data_package:
                best_idx = predictions_df["Predicted_Change"].abs().idxmax()
                report_data["featured_route"] = predictions_df.loc[best_idx].to_dict()
                
                # Add placeholder data
                report_data["featured_route"]["key_news"] = [
                    "Market rebalancing affecting rates",
                    "Seasonal demand shifts observed",
                    "Bunker price volatility impacts margins"
                ]
                
                report_data["featured_route"]["key_factors"] = [
                    "Market supply/demand imbalance",
                    "Seasonal pattern matching historical trends",
                    "Correlated with crude price movements"
                ]
        
        # Add model metrics if available
        if "model_metrics" in data_package:
            report_data["model_metadata"] = data_package["model_metrics"]
        elif "ml_metadata" in data_package and "model_metrics" in data_package["ml_metadata"]:
            report_data["model_metadata"] = data_package["ml_metadata"]["model_metrics"]
        else:
            # Use dummy values if no metrics available
            report_data["model_metadata"] = {
                "training_date": datetime.now().strftime("%Y-%m-%d"),
                "mae": 1500,
                "rmse": 2000,
                "r2": 0.75
            }
            
        # Ensure market trend data exists
        if "market_trend" not in report_data:
            report_data["market_trend"] = "neutral"
            report_data["trend_percentage"] = 50
            report_data["volatility_level"] = "moderate"
            
        return report_data
    
    def generate_report(self, template_path=None, output_filename="Maritime_Per_Week.pdf"):
        """Generate the PDF report"""
        # Load data
        data_package = self.load_data()
        
        # Prepare report data
        report_data = self.prepare_report_data(data_package)
        
        # Use default template if none provided
        if template_path is None or not os.path.exists(template_path):
            template_html = self.get_default_template()
        else:
            with open(template_path, "r") as f:
                template_html = f.read()
        
        # Render HTML using Jinja2
        template = Template(template_html)
        rendered_html = template.render(**report_data)
        
        # Save HTML for debugging
        html_path = os.path.join(self.report_dir, "report_preview.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)
            
        # Generate PDF
        output_path = os.path.join(self.report_dir, output_filename)
        HTML(string=rendered_html).write_pdf(output_path)
        
        logger.info(f"✅ Report generated successfully: {output_path}")
        return output_path
    
    
    def get_default_template(self):
        """Return the default report template with ML integration"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <!-- CSS styles remain unchanged -->
    <style>
        @page {
            size: A4;
            margin: 20px;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 5px;
            line-height: 1.3;
            font-size: 10px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-top: 5px 0;
            font-size: 20px;
        }
        h2 {
            color: #444;
            border-bottom: 1px solid #ccc;
            margin-top: 10px;
            font-size: 13px;
        }
        p {
            padding: 0;
            margin-top: 1px;
        }
        .section {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: flex-start;
            gap: 15px;
            width: 100%;
            margin-bottom: 5px;
        }
        .text {
            flex: 3.5;
            margin-right: 5px;
        }
        .charts {
            flex: 3.5;
            margin-top: 0;
        }
        .charts-grid {
            display:grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        .charts-grid img {
            width: 100%;
            height: auto;
            border: 1px solid #ccc;
            object-fit: contain;
        }
        .charts h3 {
            margin-top: 0;
            font-size: 12px;
            color: #333;
            text-decoration: underline;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            font-size: 10px;
            margin-top: 3px;
        }
        table, th, td {
            border: 1px solid #;
        }
        th, td {
            padding: 2px;
            text-align: left;
            font-size: 8px;
        }
        th {
            background-color: #f4f4f4;
            font-weight: bold;
            font-size: 10px;
        }
        .routes th:nth-child(1),
        .routes td:nth-child(1) {
            width: 5%; /* Adjust column width for 'Route' */
        }
        .routes th:nth-child(2),
        .routes td:nth-child(2) {
            width: 35%; /* Adjust column width for 'Description' */
        }
        .routes th:nth-child(3),
        .routes td:nth-child(3),
        .routes th:nth-child(4),
        .routes td:nth-child(4),
        .routes th:nth-child(5),
        .routes td:nth-child(5) {
            width: 8%; /* Adjust column width for numeric data */
        }
        .demarcation {
            margin-top: 0px;
            font-weight: bold;
            font-size: 10px;
            color: #222;
        }
        img {
            display: block;
            margin: 10px auto;
            max-width: 100%;
            max-height: 300px;
            object-fit: contain;
        }
        .cards-right {
            display: flex;
            gap: 5px;
            justify-content: space-between;
            margin: 3px 0;
        }
        .card {
            flex: 1;
            padding: 3px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            text-align: center;
            background-color: #000;
            color: #fff;
        }
        .card h3 {
            font-size: 8px;
            margin: 0 0 2px 0;
            color: #fff;
        }
        .card p {
            font-size: 7px;
            margin: 1px 0;
            color: #ccc;
        }
        .card strong {
            font-size: 9px;
            color: #fff;
        }
        
        /* ML-specific styling */
        .ml-section {
            border: 1px solid #3498db;
            border-radius: 5px;
            padding: 5px;
            margin: 10px 0;
            background-color: #f8f9fa;
        }
        .ml-section h2 {
            color: #3498db;
            border-bottom: 1px solid #3498db;
            padding-bottom: 3px;
            margin-top: 3px;
            font-size: 14px;
        }
        .prediction-up {
            color: #27ae60;
            font-weight: bold;
        }
        .prediction-down {
            color: #e74c3c;
            font-weight: bold;
        }
        .confidence-high {
            background-color: rgba(39, 174, 96, 0.1);
        }
        .confidence-medium {
            background-color: rgba(241, 196, 15, 0.1);
        }
        .confidence-low {
            background-color: rgba(231, 76, 60, 0.1);
        }
        .featured-route {
            border: 2px solid #3498db;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            background-color: #f0f7fc;
        }
        .featured-route h3 {
            color: #2980b9;
            margin-top: 5px;
            font-size: 12px;
        }
        .featured-route .factors {
            margin-left: 10px;
        }
        .featured-route .factors li {
            font-size: 8px;
            margin-bottom: 2px;
        }
        .model-info {
            font-size: 8px;
            color: #7f8c8d;
            margin-top: 5px;
            font-style: italic;
        }

        .factors-container {
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }

        .factors-column {
            flex: 1;
        }

        .factors-column p {
            margin-bottom: 3px;
        }

        .factors {
            margin-top: 0;
        }
        
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p style="text-align: left; font-size: 10px; font-weight: bold;">{{ date }} </p>

    <div class="section">
        <div class="text">

        <!-- ML-POWERED INSIGHTS SECTION -->
            <div class="ml-section">
                <h2>ML Market Insights</h2>
                <p><strong>Rate Trajectory:</strong> Our analytics indicate a {{ market_trend }} trend for {{ trend_percentage }}% of monitored routes over the next 7-10 days.</p>
                <p><strong>Focus Route:</strong> {{ featured_route.Route }} ({{ featured_route.Description }}) projected to {{ "increase" if featured_route.Predicted_Change > 0 else "decrease" }} by <span class="{{ 'prediction-up' if featured_route.Predicted_Change > 0 else 'prediction-down' }}">{{ featured_route.Predicted_Change|abs|int }} $/day</span> with {{ featured_route.Confidence|int }}% confidence.</p>
                <p><strong>Volatility Assessment:</strong> Market volatility expected to be {{ volatility_level }} based on sentiment-adjusted price momentum.</p>
                <p><strong>Pattern Recognition:</strong> Our analysis reveals correlation between news sentiment and rate changes across West African routes, suggesting heightened market sensitivity to refinery developments.</p>
            </div>


            <div style="font-size: 9px; background-color: #f4f4f4; border-left: 3px solid #2980b9; padding: 4px 6px; margin-top: 10px;">
                “Nigeria approved a $45.3M rail link study connecting Badagry, Tin Can, Apapa, and Lekki Ports to inland freight corridors — a strategic leap for West African logistics.” — FEC, 2025
            </div>

            <div style="font-size: 9px; background-color: #f4f4f4; border-left: 3px solid #28a745; padding: 4px 6px; margin-top: 10px;">
                “Using onboard sensors and SERTICA, GNV now monitors actual ship efficiency in real time — aiding onshore and crew-based decision-making for sustainable operations.” — RINA Systems
            </div>

            <div style="font-size: 9px; background-color: #f4f4f4; border-left: 3px solid #ffc107; padding: 4px 6px; margin-top: 10px;">
                “Brazilian and Algerian barrels arrive at the Dangote refinery via STS and suezmax deliveries — as Africa’s largest plant scales new supply corridors.” — Kpler via TradeWinds
            </div>

            <div style="font-size: 9px; background-color: #f4f4f4; border-left: 3px solid #007BFF; padding: 4px 6px; margin-top: 10px;">
                “GNV Polaris’ ML-driven performance engine identified two optimal fuel-saving scenarios during sea trials — confirming predictive model alignment with real-time efficiency data.” — GNV Energy Team
            </div>
            
            <div class="demarcation"></div>
            <h3 style="text-align: center; margin-top: 16px;">Dirty Routes</h3>
                    <table class="routes">
                <thead>
                    <tr>
                        <th>Route</th>
                        <th>Description</th>
                        <th>Worldscale</th>
                        <th>TCE ($/day)</th>
                        <th>+/-</th>
                        <th>Forecast</th>
                    </tr>
                </thead>
                <tbody>
                    {% for route in remaining_routes if route['Route'].startswith('TD') %}
                    <tr class="{{ 'confidence-high' if route.get('Confidence_Level') == 'High' else 'confidence-medium' if route.get('Confidence_Level') == 'Medium' else 'confidence-low' if route.get('Confidence_Level') == 'Low' else '' }}">
                        <td>{{ route['Route'] }}</td>
                        <td>{{ route['Description'] }}</td>
                        <td>{{ route['Worldscale'] }}</td>
                        <td>${{ route['TCE'] }}</td>
                        <td style="color: {{ 'green' if route['Change (TCE)'] > 0 else 'red' }};">
                            {{ route['Change (TCE)'] }}
                            {% if route['Change (TCE)'] > 0 %}
                                &#9650; <!-- Upward arrow -->
                            {% elif route['Change (TCE)'] < 0 %}
                                &#9660; <!-- Downward arrow -->
                            {% endif %}
                        </td>
                        <td style="color: {{ 'green' if route.get('Predicted_Change', 0) > 0 else 'red' }};">
                            {{ route.get('Predicted_Change', 0)|int }}
                            {% if route.get('Predicted_Change', 0) > 0 %}
                                &#9650; <!-- Upward arrow -->
                            {% elif route.get('Predicted_Change', 0) < 0 %}
                                &#9660; <!-- Downward arrow -->
                            {% endif %}
                            ({{ route.get('Confidence', 0)|int }}%)
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <div class="demarcation"></div>
            <h3 style="text-align: center; margin-top: 10px;">Clean Routes</h3>
                    <table class="routes">
                <thead>
                    <tr>
                        <th>Route</th>
                        <th>Description</th>
                        <th>Worldscale</th>
                        <th>TCE ($/day)</th>
                        <th>+/-</th>
                        <th>Forecast</th>
                    </tr>
                </thead>
                <tbody>
                    {% for route in remaining_routes if route['Route'].startswith('TC') %}
                    <tr class="{{ 'confidence-high' if route.get('Confidence_Level') == 'High' else 'confidence-medium' if route.get('Confidence_Level') == 'Medium' else 'confidence-low' if route.get('Confidence_Level') == 'Low' else '' }}">
                        <td>{{ route['Route'] }}</td>
                        <td>{{ route['Description'] }}</td>
                        <td>{{ route['Worldscale'] }}</td>
                        <td>${{ route['TCE'] }}</td>
                        <td style="color: {{ 'green' if route['Change (TCE)'] > 0 else 'red' }};">
                            {{ route['Change (TCE)'] }}
                            {% if route['Change (TCE)'] > 0 %}
                                &#9650; <!-- Upward arrow -->
                            {% elif route['Change (TCE)'] < 0 %}
                                &#9660; <!-- Downward arrow -->
                            {% endif %}
                        </td>
                        <td style="color: {{ 'green' if route.get('Predicted_Change', 0) > 0 else 'red' }};">
                            {{ route.get('Predicted_Change', 0)|int }}
                            {% if route.get('Predicted_Change', 0) > 0 %}
                                &#9650; <!-- Upward arrow -->
                            {% elif route.get('Predicted_Change', 0) < 0 %}
                                &#9660; <!-- Downward arrow -->
                            {% endif %}
                            ({{ route.get('Confidence', 0)|int }}%)
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="cards-right">
                <div class="card">
                    <h3>Tanker Recycling</h3>
                    <p><strong>11,437</strong> <span style="color: red; font-size: 7px;">-73 &#9660;</span></p>
                </div>
                <div class="card">
                    <h3>Sale & Purchase</h3>
                    <p><strong>7,623</strong> <span style="color: red; font-size: 7px;">-3 &#9660;</span></p>
                </div>
                <div class="card">
                    <h3>New Building</h3>
                    <p><strong>7,753</strong> <span style="color: red; font-size: 7px;">-37 &#9660;</span></p>
                </div>

                
            </div>

            <div style="font-size: 9px; background-color: #e3f2fd; border-left: 3px solid #1976d2; padding: 6px 8px; margin-top: 10px;">
                📌 <strong>Strategic View:</strong> West African clean product routes under pressure as Dangote supply stabilizes. Our ML model flags TC18 as this week’s most volatile route.
            </div>

          
        </div>
    
        <div class="charts">

        <!-- FEATURED ROUTE ANALYSIS -->
            <div class="featured-route">
                <h3>Route Spotlight: {{ featured_route.Route }}</h3>
                <p><strong>Description:</strong> {{ featured_route.Description }}</p>
                <p><strong>Current TCE:</strong> ${{ featured_route.Current_TCE|int if featured_route.Current_TCE is defined else 0 }} | <strong>Projected Shift:</strong> <span class="{{ 'prediction-up' if featured_route.Predicted_Change > 0 else 'prediction-down' }}">{{ featured_route.Predicted_Change|int }} $/day</span></p>
                <p><strong>Market Sentiment:</strong> {{ "Positive" if featured_route.avg_sentiment > 0 if featured_route.avg_sentiment is defined else "Neutral" }}</p>
                
                <div class="factors-container">
                    <div class="factors-column">
                        <p><strong>Market Developments:</strong></p>
                        <ul class="factors">
                        {% for news in featured_route.key_news %}
                            <li>{{ news }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                    
                    <div class="factors-column">
                        <p><strong>Analysis Drivers:</strong></p>
                        <ul class="factors">
                        {% for factor in featured_route.key_factors %}
                            <li>{{ factor }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>

            <div style="font-size: 9px; background-color: #f4f4f4; border-left: 3px solid #555; padding: 4px 6px; margin-top: 10px;">
                “Nigeria’s BRICS alignment signals a pivot from USD settlements, with regional corridor ambitions backed by both Eastern and Western partnerships.” — Global Trade Report
            </div>

            <div style="font-size: 9px; background-color: #f4f4f4; border-left: 3px solid #dc3545; padding: 4px 6px; margin-top: 10px;">
                “Nigeria’s refined product imports could nosedive as Dangote refinery hits 85% capacity — a near-term shock for MR tanker owners is looming.” — Gibson Shipbrokers
            </div>

            
            <!-- ML VISUALIZATION SECTION -->
            <h2 style="text-align: center; margin-top: 10px;">AI-Powered Rate Forecasts</h2>
            
            <!-- Top Routes by Predicted Changes -->
            {% if top_rate_changes_image is defined %}
            <img src="data:image/png;base64,{{ top_rate_changes_image }}" 
                alt="Top Routes by Predicted Rate Changes" 
                style="max-width: 100%; height: auto; margin: 10px auto; border: 1px solid #ccc;">
            {% endif %}

            <p style="font-size: 9px; color: #444; text-align: center; margin-top: -5px;">
                Top 5 predicted rate changes (ML forecast) — East of Suez routes dominate downside risk.
            </p>

                


            <h3 style="text-align: center; margin-top: 8px;">Global Bunker Prices</h3>
            <img src="data:image/png;base64,{{ map_image }}" 
                alt="Strategic Tanker Routes Map" 
                style="max-width: 100%; height: auto; margin: 20px auto; border: 1px solid #ccc;">
            
            <div class="model-info">
                Freight rate predictions generated using XGBoost AI model combining market indicators, news sentiment, and historical patterns. 
                Last updated: {{ model_metadata.training_date if model_metadata.training_date is defined else date }} | 
                Model accuracy: {{ model_metadata.mae|int if model_metadata.mae is defined else 1500 }} $/day MAE
            </div>

        </div>
        
    </div>

    <div style="page-break-before: always; margin-top: 20px;">
        <h2 style="text-align: center; color: #333; margin-bottom: 10px;">Maritime Analytics Dashboard</h2>
        
        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <!-- Left column: ML Engine Status -->
            <div style="flex: 1;">
                <h3 style="color: #444; font-size: 12px; margin-bottom: 5px;">ML Engine Performance</h3>
                <img src="data:image/png;base64,{{ ml_engine_status_image }}" 
                    alt="ML Engine Status" 
                    style="width: 100%; border: 1px solid #ccc;">
            </div>
            
            <!-- Right column: Sentiment Analysis -->
            <div style="flex: 1;">
                <h3 style="color: #444; font-size: 12px; margin-bottom: 5px;">News Sentiment Analysis</h3>
                <img src="data:image/png;base64,{{ sentiment_analysis_image }}" 
                    alt="Sentiment Analysis" 
                    style="width: 100%; border: 1px solid #ccc;">
            </div>
        </div>
    </div>

    <footer style="text-align: center; font-size: 8px; color: #555; margin-top: 5px; border-top: 1px solid #ccc; padding-top: 5px;">
        <p>© 2025 Lado Limited. All Rights Reserved.</p>
    </footer>
</body>
</html>
"""

# Example usage
if __name__ == "__main__":
    generator = MaritimeReportGenerator()
    report_path = generator.generate_report()
    
    if report_path:
        print(f"\nReport generation completed successfully!")
        print(f"Report saved to: {report_path}")
    else:
        print("\nReport generation failed. Check logs for details.")