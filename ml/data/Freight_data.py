import pandas as pd
import os
from datetime import datetime

class FreightDataProcessor:
    """
    Process and standardize freight rate data for use in ML predictions and reporting.
    """
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def process_raw_data(self, route_data):
        """
        Process raw route data, handle different formats, and standardize.
        """
        processed_data = []
        
        for item in route_data:
            # Handle different input formats
            if isinstance(item, dict):
                processed_data.append(item)
            elif isinstance(item, tuple) and len(item) >= 4:
                # Convert tuple format to dictionary
                processed_item = {
                    "Route": item[0],
                    "Description": item[1],
                    "TCE": item[4] if len(item) > 4 else None,
                    "Change (TCE)": 0  # Default value
                }
                processed_data.append(processed_item)
        
        # Convert to DataFrame
        df = pd.DataFrame(processed_data)
        
        # Ensure all required columns exist
        required_columns = ["Route", "Description", "TCE", "Change (TCE)"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
                
        # Set appropriate data types
        numeric_columns = ["TCE", "Worldscale", "Change (TCE)", "OPEX"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # Add processing metadata
        df["ProcessedDate"] = datetime.now().strftime("%Y-%m-%d")
        df["RouteType"] = df["Route"].str.slice(0, 2)
        
        # Add Nigeria relevance indicator for better filtering
        nigeria_keywords = ["Nigeria", "West Africa", "Lagos", "Lome", "Dar es Salaam"]
        df["NigeriaRelevant"] = df["Description"].str.contains('|'.join(nigeria_keywords), case=False, na=False)
        
        return df
    
    def save_data(self, df, filename="freight_rates.csv"):
        """Save processed data to CSV"""
        output_path = os.path.join(self.output_dir, filename)
        df.to_csv(output_path, index=False)
        print(f"✅ Freight data saved to: {output_path}")
        return output_path
        
    def load_data(self, filename="freight_rates.csv"):
        """Load processed data from CSV"""
        input_path = os.path.join(self.output_dir, filename)
        if os.path.exists(input_path):
            return pd.read_csv(input_path)
        else:
            print(f"❌ File not found: {input_path}")
            return None
            
    def get_route_mapping(self):
        """Return mapping of route codes to descriptions for reference"""
        return {
            "TD2": "Middle East Gulf to Singapore",
            "TD3C": "Middle East Gulf to China (VLCC)",
            "TD6": "Black Sea to Mediterranean (Suezmax)",
            "TD7": "North Sea to Continent (Aframax)",
            "TD8": "Kuwait to Singapore",
            "TD9": "Caribbean to US Gulf (LR1)",
            "TD15": "West Africa to China (VLCC)",
            "TD20": "West Africa to UK-Continent (Suezmax)",
            "TD22": "US Gulf to China",
            "TD25": "US Gulf to UK-Continent",
            "TD27": "Guyana to ARA",
            "TC5": "CPP Middle East Gulf to Japan (LR1)",
            "TC8": "CPP Middle East Gulf to UK-Continent (LR1)",
            "TC12": "Naphtha West Coast India to Japan (MR)",
            "TC15": "Naphtha Mediterranean to Far East (Aframax)",
            "TC16": "ARA to Offshore Lome (LR1)",
            "TC17": "CPP Jubail to Dar es Salaam (MR)",
            "TC18": "CPP US Gulf to Brazil (MR)",
            "TC19": "CPP Amsterdam to Lagos (MR)",
            "TC20": "CPP Middle East Gulf to UK-Continent (Aframax)",
            "TC21": "CPP US Gulf to Caribbean",
            "TC23": "CPP/UNL/ULSD ARA to UK-Cont"
        }

# Example usage
if __name__ == "__main__":
    # Define the freight data (with mix of dictionaries and tuples to demonstrate handling)
    full_route_data = [
        {"Route": "TD2", "Description": "270K Middle East Gulf to Singapore", "Worldscale": 78.00, "TCE": 60328, "Change (TCE)": 183, "OPEX": 8080},
        {"Route": "TD3C", "Description": "270K Middle East Gulf to China (VLCC)", "Worldscale": 77.15, "TCE": 57589, "Change (TCE)": 698, "OPEX": 8080},
        # Rest of your routes...
        {"Route": "TC20", "Description": "90K CPP Middle East Gulf to UK-Continent (Aframax)", "Worldscale": 3956250, "TCE": 36279, "Change (TCE)": 2492, "OPEX": 7030},
        # Handle tuples format
        ("TC21", "CPP US Gulf to Caribbean (Houston to Pozos Colorados)", "5/10 days", "Clean Petroleum Products", 38000, 15, 3.75, True),
        ("TC23", "CPP/UNL/ULSD middle distillate. ARA to UK-Cont (Amsterdam to Le Havre)", "5/10 days", "Clean Petroleum Products", 30000, 15, 3.75, True)
    ]
    
    # Process and save
    processor = FreightDataProcessor()
    df = processor.process_raw_data(full_route_data)
    processor.save_data(df)
    
    # Print confirmation
    print(f"Processed {len(df)} routes, including {df['NigeriaRelevant'].sum()} Nigeria-relevant routes")