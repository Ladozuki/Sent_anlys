import os
import argparse
import logging
import time
from datetime import datetime

# Import our modules
from data.freight_data import FreightDataProcessor
from data.mktdata import MarketDataCollector
from utils.data_adpt import MarketDataAdapter
from data.macrodata import MacroDataCollector
from data.news_sent import NewsSentimentCollector
from utils.predictionengine import MaritimeMLEngine
from utils.report_gen import MaritimeReportGenerator

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"maritime_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MaritimePipeline")

class MaritimePipeline:
    """
    Orchestrates the entire Maritime ML Pipeline from data collection to report generation.
    """
    def __init__(self, data_dir="data", results_dir="results", models_dir="models", 
                 reports_dir="reports", images_dir="images", 
                 use_existing_data=False):
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.models_dir = models_dir
        self.reports_dir = reports_dir
        self.images_dir = images_dir
        self.use_existing_data = use_existing_data
        
        # Create all required directories
        for directory in [data_dir, results_dir, models_dir, reports_dir, images_dir]:
            os.makedirs(directory, exist_ok=True)
            
        # Initialize components
        self.freight_processor = FreightDataProcessor(output_dir=data_dir)
        
        # Choose appropriate data collectors based on flags
        if use_existing_data:
            logger.info("Using existing data files (no API calls)")
            self.market_collector = MarketDataAdapter(data_dir=data_dir)
            self.macro_collector = None  # Skip macro collection
            self.news_collector = None   # Skip news collection
        else:
            # Use live data collectors with embedded API keys
            self.market_collector = MarketDataCollector(output_dir=data_dir)
            self.macro_collector = MacroDataCollector(output_dir=data_dir)
            self.news_collector = NewsSentimentCollector(output_dir=data_dir)
        
        self.ml_engine = MaritimeMLEngine(
            data_dir=data_dir, 
            results_dir=results_dir, 
            models_dir=models_dir
        )
        
        self.report_generator = MaritimeReportGenerator(
            data_dir=data_dir,
            results_dir=results_dir,
            report_dir=reports_dir,
            images_dir=images_dir
        )
    
    def verify_existing_data(self):
        """Verify that all required data files exist"""
        required_files = [
            os.path.join(self.data_dir, "freight_rates.csv"),
            os.path.join(self.data_dir, "maritime_data_2025.csv"),
            os.path.join(self.data_dir, "maritime_data_2024.csv")
        ]
        
        optional_files = [
            os.path.join(self.data_dir, "news_sentiment.csv"),
            os.path.join(self.data_dir, "combined_indicators.csv")
        ]
        
        # Check required files
        missing_required = [f for f in required_files if not os.path.exists(f)]
        if missing_required:
            for f in missing_required:
                logger.error(f"Required data file missing: {f}")
            return False
            
        # Check optional files
        missing_optional = [f for f in optional_files if not os.path.exists(f)]
        if missing_optional:
            for f in missing_optional:
                logger.warning(f"Optional data file missing: {f}")
                
        logger.info("Data verification complete. All required files present.")
        return True
    
    def run_data_collection(self, skip_market=False, skip_macro=False, skip_news=False):
        """Run the data collection phase or verify existing data"""
        logger.info("Starting data collection phase...")
        start_time = time.time()
        
        # If using existing data, verify files instead of collecting
        if self.use_existing_data:
            logger.info("Using existing data files. Verifying files...")
            if not self.verify_existing_data():
                logger.error("Data verification failed. Some required files are missing.")
                return {}
                
            # Just return paths to existing files
            return {
                "freight_path": os.path.join(self.data_dir, "freight_rates.csv"),
                "market_path": os.path.join(self.data_dir, "maritime_data_2025.csv"),
                "news_path": os.path.join(self.data_dir, "news_sentiment.csv") 
                              if os.path.exists(os.path.join(self.data_dir, "news_sentiment.csv")) else None
            }
        
        # Process freight data
        logger.info("Processing freight data...")
        full_route_data = [
            {"Route": "TD2", "Description": "270K Middle East Gulf to Singapore", "Worldscale": 78.00, "TCE": 60328, "Change (TCE)": 183, "OPEX": 8080},
            {"Route": "TD3C", "Description": "270K Middle East Gulf to China (VLCC)", "Worldscale": 77.15, "TCE": 57589, "Change (TCE)": 698, "OPEX": 8080},
            # ... other routes (abbreviated for clarity)
            {"Route": "TC23", "Description": "CPP/UNL/ULSD middle distillate. ARA to UK-Cont (Amsterdam to Le Havre)", "Worldscale": 199.06, "TCE": 30000, "Change (TCE)": 15, "OPEX": 6876}
        ]
        
        freight_df = self.freight_processor.process_raw_data(full_route_data)
        freight_path = self.freight_processor.save_data(freight_df)
        
        # Collect market data (optional)
        if not skip_market:
            logger.info("Collecting market data...")
            market_path = self.market_collector.run_collection()
        else:
            logger.info("Skipping market data collection.")
            market_path = None
            
        # Collect macro data (optional)
        if not skip_macro and self.macro_collector:
            logger.info("Collecting macroeconomic data...")
            indicators = self.macro_collector.fetch_all_indicators()
            self.macro_collector.create_correlation_matrix()
        else:
            logger.info("Skipping macro data collection.")
            
        # Collect news sentiment data (optional)
        if not skip_news and self.news_collector:
            logger.info("Collecting news sentiment data...")
            news_path = self.news_collector.collect_news(days_back=30)
        else:
            logger.info("Skipping news sentiment collection.")
            news_path = None
            
        elapsed_time = time.time() - start_time
        logger.info(f"Data collection completed in {elapsed_time:.2f} seconds")
        
        return {
            "freight_path": freight_path,
            "market_path": market_path,
            "news_path": news_path
        }
        
    def run_ml_pipeline(self):
        """Run the ML pipeline"""
        logger.info("Starting ML pipeline...")
        start_time = time.time()
        
        # Run the ML pipeline
        ml_output = self.ml_engine.run_pipeline()
        
        if ml_output is None:
            logger.error("ML pipeline failed")
            return False
            
        elapsed_time = time.time() - start_time
        logger.info(f"ML pipeline completed in {elapsed_time:.2f} seconds")
        
        return ml_output
        
    def generate_report(self):
        """Generate the final report"""
        logger.info("Generating final report...")
        start_time = time.time()
        
        # Generate report
        report_path = self.report_generator.generate_report()
        
        if not report_path:
            logger.error("Report generation failed")
            return False
            
        elapsed_time = time.time() - start_time
        logger.info(f"Report generation completed in {elapsed_time:.2f} seconds")
        
        return report_path
        
    def run_full_pipeline(self, skip_market=False, skip_macro=False, skip_news=False, skip_ml=False):
        """Run the complete pipeline"""
        logger.info("Starting full maritime ML pipeline...")
        total_start_time = time.time()
        
        # 1. Data Collection or Verification
        collection_result = self.run_data_collection(skip_market, skip_macro, skip_news)
        
        if not collection_result:
            logger.error("Data collection/verification failed. Cannot continue pipeline.")
            return None
        
        # 2. ML Pipeline (optional)
        if not skip_ml:
            ml_output = self.run_ml_pipeline()
            if not ml_output:
                logger.warning("ML pipeline failed, continuing with report generation")
        else:
            logger.info("Skipping ML pipeline")
            
        # 3. Report Generation
        report_path = self.generate_report()
        
        total_elapsed_time = time.time() - total_start_time
        
        if report_path:
            logger.info(f"✅ Full pipeline completed successfully in {total_elapsed_time:.2f} seconds")
            logger.info(f"Final report: {report_path}")
            return report_path
        else:
            logger.error(f"❌ Pipeline failed after {total_elapsed_time:.2f} seconds")
            return None

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Maritime ML Pipeline Controller")
    
    parser.add_argument("--use-existing-data", action="store_true", 
                       help="Use existing data files (no API calls)")
    parser.add_argument("--skip-market", action="store_true", help="Skip market data collection")
    parser.add_argument("--skip-macro", action="store_true", help="Skip macroeconomic data collection")
    parser.add_argument("--skip-news", action="store_true", help="Skip news sentiment collection")
    parser.add_argument("--skip-ml", action="store_true", help="Skip ML pipeline")
    parser.add_argument("--output", type=str, default="Maritime_Per_Week.pdf", help="Output report filename")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    pipeline = MaritimePipeline(
        use_existing_data=args.use_existing_data
    )
    
    report_path = pipeline.run_full_pipeline(
        skip_market=args.skip_market,
        skip_macro=args.skip_macro,
        skip_news=args.skip_news,
        skip_ml=args.skip_ml
    )
    
    if report_path:
        print(f"\nPipeline completed successfully!")
        print(f"Report saved to: {report_path}")
    else:
        print("\nPipeline failed. Check logs for details.")