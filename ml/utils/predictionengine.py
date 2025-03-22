import os
import numpy as np
import pandas as pd
import xgboost as xgb
from datetime import datetime, timedelta
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("maritime_ml.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MaritimeMLEngine")

class MaritimeMLEngine:
    """
    ML prediction engine for maritime shipping rates and market trends.
    Uses XGBoost for transparent, effective predictions without unnecessary complexity.
    """
    def __init__(self, data_dir="data", results_dir="results", models_dir="models"):
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.models_dir = models_dir
        
        # Create directories if they don't exist
        for directory in [data_dir, results_dir, models_dir]:
            os.makedirs(directory, exist_ok=True)
            
        self.model = None
        self.feature_importance = None
        self.scaler = None
        self.train_metrics = None
        self.available_features = []
        
    def load_data(self):
        """Load and merge all necessary data for modeling"""
        # Load freight rates
        freight_path = os.path.join(self.data_dir, "freight_rates.csv")
        if not os.path.exists(freight_path):
            logger.error(f"Freight data file not found: {freight_path}")
            return None
            
        freight_df = pd.read_csv(freight_path)
        
        # Load market data
        market_path = os.path.join(self.data_dir, "maritime_data_2025.csv")
        if not os.path.exists(market_path):
            logger.warning(f"Market data file not found: {market_path}")
            market_df = None
        else:
            market_df = pd.read_csv(market_path)
            
        # Load news sentiment data
        news_path = os.path.join(self.data_dir, "news_sentiment.csv")
        if not os.path.exists(news_path):
            logger.warning(f"News sentiment file not found: {news_path}")
            news_df = None
        else:
            news_df = pd.read_csv(news_path)
            
        # Load macro indicators if available
        indicators_path = os.path.join(self.data_dir, "combined_indicators.csv")
        if not os.path.exists(indicators_path):
            logger.warning(f"Indicators file not found: {indicators_path}")
            indicators_df = None
        else:
            indicators_df = pd.read_csv(indicators_path)
        
        return {
            "freight": freight_df,
            "market": market_df,
            "news": news_df,
            "indicators": indicators_df
        }
    
    def prepare_features(self, data_dict):
        """Prepare features for model training"""
        if data_dict is None or "freight" not in data_dict:
            logger.error("Invalid data dictionary provided")
            return None, None
            
        freight_df = data_dict["freight"]
        
        # Initialize feature DataFrame with route info
        features_df = pd.DataFrame({
            "Route": freight_df["Route"],
            "RouteType": freight_df["Route"].str.slice(0, 2)  # TC or TD
        })
        
        # Add one-hot encoding for route types
        features_df = pd.get_dummies(features_df, columns=["RouteType"], drop_first=False)
        
        # Add current TCE and WS as features
        if "TCE" in freight_df.columns:
            features_df["Current_TCE"] = freight_df["TCE"]
        
        if "Worldscale" in freight_df.columns:
            features_df["Current_WS"] = freight_df["Worldscale"]
            
        if "OPEX" in freight_df.columns:
            features_df["OPEX"] = freight_df["OPEX"]
            features_df["TCE_OPEX_Ratio"] = freight_df["TCE"] / freight_df["OPEX"]
        
        # Add Nigeria relevance if available
        if "NigeriaRelevant" in freight_df.columns:
            features_df["NigeriaRelevant"] = freight_df["NigeriaRelevant"].astype(int)
        
        # Process news sentiment if available
        if "news" in data_dict and data_dict["news"] is not None:
            news_df = data_dict["news"]
            
            # Check if the news data has the needed columns
            if "clean_topic" in news_df.columns and "sentiment_score" in news_df.columns:
                # Calculate sentiment metrics per route
                sentiment_metrics = {}
                
                for route in freight_df["Route"]:
                    route_news = news_df[news_df["clean_topic"] == route]
                    
                    if len(route_news) > 0:
                        metrics = {
                            f"{route}_avg_sentiment": route_news["sentiment_score"].mean(),
                            f"{route}_pos_news_count": (route_news["sentiment_score"] > 0.1).sum(),
                            f"{route}_neg_news_count": (route_news["sentiment_score"] < -0.1).sum(),
                            f"{route}_news_count": len(route_news)
                        }
                    else:
                        metrics = {
                            f"{route}_avg_sentiment": 0,
                            f"{route}_pos_news_count": 0,
                            f"{route}_neg_news_count": 0,
                            f"{route}_news_count": 0
                        }
                        
                    sentiment_metrics[route] = metrics
                
                # Add to features DataFrame
                for route, metrics in sentiment_metrics.items():
                    route_mask = features_df["Route"] == route
                    for metric_name, value in metrics.items():
                        # Use generic column names instead of route-specific
                        generic_name = metric_name.split("_", 1)[1]  # Remove route prefix
                        features_df.loc[route_mask, generic_name] = value
        
        # Process market data if available
        if "market" in data_dict and data_dict["market"] is not None:
            market_df = data_dict["market"]
            
            # Extract latest market values for key symbols
            key_symbols = ['FRO', 'GLNG', 'TK', 'CL=F', 'BZ=F', 'STNG', 'GC=F', 'SI=F']
            available_symbols = [s for s in key_symbols if s in market_df["Symbol"].unique()]
            
            if available_symbols:
                # Get latest close prices
                latest_prices = {}
                for symbol in available_symbols:
                    symbol_data = market_df[market_df["Symbol"] == symbol]
                    if not symbol_data.empty:
                        latest_date = symbol_data["Date"].max()
                        latest_price = symbol_data[symbol_data["Date"] == latest_date]["Close"].values[0]
                        latest_prices[symbol] = latest_price
                
                # Add market data as global features (same for all routes)
                for symbol, price in latest_prices.items():
                    features_df[f"{symbol}_price"] = price
            
            # Add YTD changes if available
            if "YTD_Change_Pct" in market_df.columns:
                for symbol in available_symbols:
                    symbol_data = market_df[market_df["Symbol"] == symbol]
                    if not symbol_data.empty and not symbol_data["YTD_Change_Pct"].isna().all():
                        ytd_change = symbol_data["YTD_Change_Pct"].iloc[0]
                        features_df[f"{symbol}_ytd_change"] = ytd_change
        
        # Process macro indicators if available
        if "indicators" in data_dict and data_dict["indicators"] is not None:
            indicators_df = data_dict["indicators"]
            
            # Get latest values for each indicator
            if not indicators_df.empty:
                latest_indicators = {}
                
                for metric in indicators_df["metric"].unique():
                    metric_data = indicators_df[indicators_df["metric"] == metric]
                    if not metric_data.empty:
                        latest_date = metric_data["date"].max()
                        latest_value = metric_data[metric_data["date"] == latest_date]["value"].values[0]
                        latest_indicators[metric] = latest_value
                
                # Add indicators as global features
                for metric, value in latest_indicators.items():
                    safe_name = metric.lower().replace(" ", "_")
                    features_df[safe_name] = value
        
        # Target variable is the TCE change
        target = freight_df["Change (TCE)"] if "Change (TCE)" in freight_df.columns else None
        
        # Store available features for later reference
        self.available_features = list(features_df.columns.drop("Route") if "Route" in features_df.columns else features_df.columns)
        
        # Return features and target
        return features_df, target
    
    def train_model(self, features, target, test_size=0.2, random_state=42):
        """Train an XGBoost model on the prepared features"""
        if features is None or target is None:
            logger.error("Features or target is None, cannot train model")
            return False
            
        # Split into train and test sets
        X = features.drop("Route", axis=1) if "Route" in features.columns else features
        y = target
        
        # Handle empty dataset
        if len(X) == 0:
            logger.error("Empty feature set, cannot train model")
            return False
            
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        self.model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # Save metrics
        self.train_metrics = {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "training_date": datetime.now().strftime("%Y-%m-%d"),
            "data_points": len(X),
            "features": len(X.columns)
        }
        
        # Get feature importance
        importance = self.model.feature_importances_
        self.feature_importance = dict(zip(X.columns, importance))
        
        # Save model and metadata
        self.save_model()
        
        logger.info(f"Model trained successfully: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.2f}")
        return True
    
    def save_model(self):
        """Save the trained model and metadata"""
        if self.model is None:
            logger.warning("No model to save")
            return False
            
        # Save XGBoost model
        model_path = os.path.join(self.models_dir, "maritime_xgb_model.json")
        self.model.save_model(model_path)
        
        # Save scaler
        scaler_path = os.path.join(self.models_dir, "feature_scaler.pkl")
        joblib.dump(self.scaler, scaler_path)
        
        # Save feature importance
        importance_path = os.path.join(self.models_dir, "feature_importance.json")
        with open(importance_path, "w") as f:
            json.dump(self.feature_importance, f, indent=2)
            
        # Save training metrics
        metrics_path = os.path.join(self.models_dir, "training_metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(self.train_metrics, f, indent=2)
            
        # Save available features
        features_path = os.path.join(self.models_dir, "available_features.json")
        with open(features_path, "w") as f:
            json.dump(self.available_features, f, indent=2)
            
        logger.info(f"Model and metadata saved to {self.models_dir}")
        return True
    
    def load_model(self):
        """Load a previously trained model"""
        model_path = os.path.join(self.models_dir, "maritime_xgb_model.json")
        scaler_path = os.path.join(self.models_dir, "feature_scaler.pkl")
        importance_path = os.path.join(self.models_dir, "feature_importance.json")
        metrics_path = os.path.join(self.models_dir, "training_metrics.json")
        features_path = os.path.join(self.models_dir, "available_features.json")
        
        # Check if all files exist
        if not all(os.path.exists(p) for p in [model_path, scaler_path, importance_path, metrics_path, features_path]):
            logger.warning("One or more model files missing, cannot load model")
            return False
            
        try:
            # Load model
            self.model = xgb.XGBRegressor()
            self.model.load_model(model_path)
            
            # Load scaler
            self.scaler = joblib.load(scaler_path)
            
            # Load feature importance
            with open(importance_path, "r") as f:
                self.feature_importance = json.load(f)
                
            # Load training metrics
            with open(metrics_path, "r") as f:
                self.train_metrics = json.load(f)
                
            # Load available features
            with open(features_path, "r") as f:
                self.available_features = json.load(f)
                
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def generate_predictions(self):
        """Generate predictions for current freight rates"""
        # Load data
        data_dict = self.load_data()
        if data_dict is None:
            logger.error("Failed to load data for predictions")
            return None
            
        # Prepare features (without target for prediction)
        features, _ = self.prepare_features(data_dict)
        if features is None:
            logger.error("Failed to prepare features for prediction")
            return None
            
        # Load model if not already loaded
        if self.model is None:
            if not self.load_model():
                logger.error("Failed to load model for prediction")
                return None
        
        # Extract routes for results
        routes = features["Route"].values
        
        # Prepare feature matrix without route column
        X = features.drop("Route", axis=1) if "Route" in features.columns else features
        
        # Align features with model's expected features
        missing_cols = set(self.available_features) - set(X.columns)
        for col in missing_cols:
            X[col] = 0  # Fill with 0 for missing features
            
        # Select only the features the model was trained on
        X = X[self.available_features]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Generate predictions
        predictions = self.model.predict(X_scaled)
        
        # Calculate prediction intervals (simple method)
        prediction_std = np.std(predictions)
        lower_bounds = predictions - 1.96 * prediction_std
        upper_bounds = predictions + 1.96 * prediction_std
        
        # Create results DataFrame
        results_df = pd.DataFrame({
            "Route": routes,
            "Predicted_Change": predictions,
            "Lower_Bound": lower_bounds,
            "Upper_Bound": upper_bounds,
            "Prediction_Date": datetime.now().strftime("%Y-%m-%d")
        })
        
        # Add route descriptions
        freight_df = data_dict["freight"]
        if "Description" in freight_df.columns:
            route_descriptions = dict(zip(freight_df["Route"], freight_df["Description"]))
            results_df["Description"] = results_df["Route"].map(route_descriptions)
        
        # Add current TCE values if available
        if "TCE" in freight_df.columns:
            current_tce = dict(zip(freight_df["Route"], freight_df["TCE"]))
            results_df["Current_TCE"] = results_df["Route"].map(current_tce)
            results_df["Predicted_TCE"] = results_df["Current_TCE"] + results_df["Predicted_Change"]
        
        # Add last change values if available
        if "Change (TCE)" in freight_df.columns:
            last_change = dict(zip(freight_df["Route"], freight_df["Change (TCE)"]))
            results_df["Last_Change"] = results_df["Route"].map(last_change)
        
        # Calculate confidence (simple method - inverse of interval width relative to prediction magnitude)
        interval_width = results_df["Upper_Bound"] - results_df["Lower_Bound"]
        prediction_magnitude = results_df["Predicted_Change"].abs() + 100  # Add 100 to avoid division by near-zero
        results_df["Confidence"] = 100 * (1 - interval_width / (2 * prediction_magnitude))
        results_df["Confidence"] = results_df["Confidence"].clip(0, 100)  # Clip to 0-100 range
        
        # Add trend direction
        results_df["Trend"] = np.where(results_df["Predicted_Change"] > 0, "Improving", "Declining")
        
        # Add confidence level category
        results_df["Confidence_Level"] = pd.cut(
            results_df["Confidence"], 
            bins=[0, 60, 80, 100], 
            labels=["Low", "Medium", "High"]
        )
        
        # Sort by predicted change (descending)
        results_df = results_df.sort_values("Predicted_Change", ascending=False)
        
        # Save predictions
        predictions_path = os.path.join(self.results_dir, "route_predictions.csv")
        results_df.to_csv(predictions_path, index=False)
        logger.info(f"Predictions saved to {predictions_path}")
        
        return results_df
    
    def generate_visualizations(self, predictions_df):
        """Generate visualizations for the predictions"""
        if predictions_df is None or predictions_df.empty:
            logger.warning("No predictions available for visualization")
            return {}
            
        # Create visualizations directory
        viz_dir = os.path.join(self.results_dir, "visuals")
        os.makedirs(viz_dir, exist_ok=True)
        
        visualization_paths = {}
        
        try:
            # 1. Top Routes by Predicted Change
            plt.figure(figsize=(12, 8))
            
            # Select top 5 and bottom 5 routes by predicted change
            top_routes = pd.concat([
                predictions_df.head(5),  # Top 5 improving
                predictions_df.tail(5)   # Top 5 declining
            ])
            
            # Create bar chart
            colors = ['green' if x > 0 else 'red' for x in top_routes['Predicted_Change']]
            plt.bar(range(len(top_routes)), top_routes['Predicted_Change'], color=colors)
            
            # Add error bars for uncertainty
            plt.errorbar(
                range(len(top_routes)), 
                top_routes['Predicted_Change'],
                yerr=[
                    top_routes['Predicted_Change'] - top_routes['Lower_Bound'],
                    top_routes['Upper_Bound'] - top_routes['Predicted_Change']
                ],
                fmt='none', 
                color='black', 
                capsize=5
            )
            
            plt.xticks(range(len(top_routes)), top_routes['Route'], rotation=45, ha='right')
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            plt.xlabel('Route')
            plt.ylabel('Predicted TCE Change ($/day)')
            plt.title('Top Routes by Predicted Rate Changes')
            plt.tight_layout()
            
            # Save figure
            top_rates_path = os.path.join(viz_dir, 'top_rate_changes.png')
            plt.savefig(top_rates_path, dpi=300, bbox_inches='tight')
            visualization_paths['top_rate_changes'] = top_rates_path
            plt.close()
            
            # 2. Current vs Predicted TCE Rates 
            if "Current_TCE" in predictions_df.columns and "Predicted_TCE" in predictions_df.columns:
                plt.figure(figsize=(14, 8))
                
                # Sort routes by current TCE
                route_order = predictions_df.sort_values('Current_TCE', ascending=False)['Route']
                
                current_tce = [predictions_df[predictions_df['Route'] == route]['Current_TCE'].values[0] 
                               for route in route_order]
                predicted_tce = [predictions_df[predictions_df['Route'] == route]['Predicted_TCE'].values[0] 
                                 for route in route_order]
                
                x = np.arange(len(route_order))
                width = 0.35
                
                fig, ax = plt.subplots(figsize=(14, 8))
                rects1 = ax.bar(x - width/2, current_tce, width, label='Current TCE')
                rects2 = ax.bar(x + width/2, predicted_tce, width, label='Predicted TCE')
                
                ax.set_ylabel('TCE Rate ($/day)')
                ax.set_title('Current vs Predicted TCE Rates by Route')
                ax.set_xticks(x)
                ax.set_xticklabels(route_order, rotation=45, ha='right')
                ax.legend()
                
                # Add value labels on bars
                def autolabel(rects):
                    for rect in rects:
                        height = rect.get_height()
                        ax.annotate(f'${int(height)}',
                                    xy=(rect.get_x() + rect.get_width()/2, height),
                                    xytext=(0, 3),
                                    textcoords="offset points",
                                    ha='center', va='bottom', fontsize=8)
                
                autolabel(rects1)
                autolabel(rects2)
                
                fig.tight_layout()
                
                # Save figure
                tce_comparison_path = os.path.join(viz_dir, 'tce_comparison.png')
                plt.savefig(tce_comparison_path, dpi=300, bbox_inches='tight')
                visualization_paths['tce_comparison'] = tce_comparison_path
                plt.close()
            
            # 3. Feature Importance Plot
            if self.feature_importance:
                plt.figure(figsize=(12, 8))
                
                # Sort feature importance
                sorted_importance = dict(sorted(self.feature_importance.items(), 
                                               key=lambda x: x[1], reverse=True))
                
                # Take top 15 features
                top_features = dict(list(sorted_importance.items())[:15])
                
                plt.barh(list(top_features.keys()), list(top_features.values()))
                plt.xlabel('Importance')
                plt.title('Top 15 Feature Importance')
                plt.tight_layout()
                
                # Save figure
                importance_path = os.path.join(viz_dir, 'feature_importance.png')
                plt.savefig(importance_path, dpi=300, bbox_inches='tight')
                visualization_paths['feature_importance'] = importance_path
                plt.close()
                
            # 4. Prediction Uncertainty by Route
            plt.figure(figsize=(12, 6))
            
            # Calculate uncertainty magnitude
            uncertainty = predictions_df["Upper_Bound"] - predictions_df["Lower_Bound"]
            
            # Sort by uncertainty
            sorted_indices = uncertainty.argsort()
            sorted_routes = predictions_df.iloc[sorted_indices]["Route"].values
            sorted_uncertainty = uncertainty.iloc[sorted_indices].values
            
            # Create horizontal bar chart
            plt.barh(range(len(sorted_routes)), sorted_uncertainty)
            plt.yticks(range(len(sorted_routes)), sorted_routes)
            plt.xlabel('Prediction Uncertainty Range')
            plt.title('Route Prediction Confidence (Smaller is Better)')
            plt.tight_layout()
            
            # Save figure
            uncertainty_path = os.path.join(viz_dir, 'prediction_uncertainty.png')
            plt.savefig(uncertainty_path, dpi=300, bbox_inches='tight')
            visualization_paths['prediction_uncertainty'] = uncertainty_path
            plt.close()
            
            logger.info(f"✅ Generated {len(visualization_paths)} visualizations")
            return visualization_paths
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            return visualization_paths
    
    def generate_market_analysis(self, predictions_df):
        """Generate market analysis for the report"""
        if predictions_df is None or predictions_df.empty:
            return {
                "market_trend": "neutral",
                "trend_percentage": 50,
                "volatility_level": "moderate",
                "key_insight": "Insufficient data for market analysis"
            }
            
        # Calculate overall market trend
        improving_routes = (predictions_df["Predicted_Change"] > 0).sum()
        total_routes = len(predictions_df)
        improving_percentage = int((improving_routes / total_routes) * 100)
        
        if improving_percentage > 65:
            market_trend = "strongly positive"
        elif improving_percentage > 50:
            market_trend = "moderately positive"
        elif improving_percentage < 35:
            market_trend = "strongly negative"
        elif improving_percentage < 50:
            market_trend = "moderately negative"
        else:
            market_trend = "neutral"
            
        # Calculate volatility level based on prediction intervals
        avg_uncertainty = (predictions_df["Upper_Bound"] - predictions_df["Lower_Bound"]).mean()
        avg_change_magnitude = predictions_df["Predicted_Change"].abs().mean()
        
        volatility_ratio = avg_uncertainty / (avg_change_magnitude + 100)  # Add 100 to avoid division by small numbers
        
        if volatility_ratio > 1.5:
            volatility_level = "high"
        elif volatility_ratio > 0.8:
            volatility_level = "moderate"
        else:
            volatility_level = "low"
            
        # Identify featured route (largest predicted change with good confidence)
        high_confidence_routes = predictions_df[predictions_df["Confidence"] > 70]
        
        if not high_confidence_routes.empty:
            # Find route with largest absolute change
            featured_idx = high_confidence_routes["Predicted_Change"].abs().idxmax()
            featured_route = high_confidence_routes.loc[featured_idx].to_dict()
        else:
            # If no high confidence predictions, use the largest change
            featured_idx = predictions_df["Predicted_Change"].abs().idxmax()
            featured_route = predictions_df.loc[featured_idx].to_dict()
            
        # Generate key driving factors (placeholder - would need more data integration)
        key_factors = [
            "Dangote refinery impact on regional product flows",
            "Shifting crude supply patterns from West Africa",
            "Port infrastructure development in Nigeria",
            "Global oil price volatility"
        ]
        
        return {
            "market_trend": market_trend,
            "trend_percentage": improving_percentage,
            "volatility_level": volatility_level,
            "featured_route": featured_route,
            "key_factors": key_factors
        }
    
    def run_pipeline(self):
        """Run the complete ML pipeline"""
        # 1. Load data
        logger.info("Loading data...")
        data_dict = self.load_data()
        
        if data_dict is None:
            logger.error("Failed to load data")
            return None
            
        # 2. Prepare features
        logger.info("Preparing features...")
        features, target = self.prepare_features(data_dict)
        
        if features is None or target is None:
            logger.error("Failed to prepare features")
            return None
            
        # 3. Train model
        logger.info("Training model...")
        if not self.train_model(features, target):
            logger.error("Failed to train model")
            return None
            
        # 4. Generate predictions
        logger.info("Generating predictions...")
        predictions_df = self.generate_predictions()
        
        if predictions_df is None:
            logger.error("Failed to generate predictions")
            return None
            
        # 5. Generate visualizations
        logger.info("Generating visualizations...")
        visualization_paths = self.generate_visualizations(predictions_df)
        
        # 6. Generate market analysis
        logger.info("Generating market analysis...")
        market_analysis = self.generate_market_analysis(predictions_df)
        
        # 7. Prepare output package
        output_package = {
            "predictions": predictions_df,
            "visualizations": visualization_paths,
            "model_metrics": self.train_metrics,
            "feature_importance": self.feature_importance,
            "market_analysis": market_analysis
        }
        
        # Save output package metadata
        metadata_path = os.path.join(self.results_dir, "ml_output_metadata.json")
        
        serializable_package = {
            "run_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "routes_analyzed": len(predictions_df),
            "model_metrics": self.train_metrics,
            "visualization_paths": visualization_paths,
            "market_analysis": {
                k: v for k, v in market_analysis.items() 
                if k != "featured_route"  # Skip the route dict for serializability
            }
        }
        
        with open(metadata_path, "w") as f:
            json.dump(serializable_package, f, indent=2)
            
        logger.info(f"✅ ML pipeline completed successfully, results saved to {self.results_dir}")
        return output_package

# Example usage
if __name__ == "__main__":
    ml_engine = MaritimeMLEngine()
    output = ml_engine.run_pipeline()
    
    if output is not None:
        print("\nPipeline completed successfully!")
        print(f"Model metrics: MAE={output['model_metrics']['mae']:.2f}, R²={output['model_metrics']['r2']:.2f}")
        print(f"Routes analyzed: {len(output['predictions'])}")
        print(f"Market trend: {output['market_analysis']['market_trend']}")
        print(f"Featured route: {output['market_analysis']['featured_route']['Route']}")
    else:
        print("\nPipeline failed. Check logs for details.")