import os
import argparse
import logging
import time
from datetime import datetime

# Import our modules
from data.freight_data import FreightDataProcessor
from data.mktdata import MarketDataCollector
from utils.data_adpt import MarketDataAdapter  # New adapter
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
                 alpha_vantage_key=None, news_api_key=None,
                 use_local_market_data=False):  # Added option for local market data
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.models_dir = models_dir
        self.reports_dir = reports_dir
        self.images_dir = images_dir
        self.alpha_vantage_key = alpha_vantage_key
        self.news_api_key = news_api_key
        self.use_local_market_data = use_local_market_data
        
        # Create all required directories
        for directory in [data_dir, results_dir, models_dir, reports_dir, images_dir]:
            os.makedirs(directory, exist_ok=True)
            
        # Initialize components
        self.freight_processor = FreightDataProcessor(output_dir=data_dir)
        
        # Choose between adapter and collector for market data
        if use_local_market_data:
            self.market_collector = MarketDataAdapter(data_dir=data_dir)
            logger.info("Using local market data files")
        else:
            self.market_collector = MarketDataCollector(output_dir=data_dir)
            logger.info("Using yfinance API for market data")
        
        if alpha_vantage_key:
            self.macro_collector = MacroDataCollector(alpha_vantage_key, output_dir=data_dir)
        else:
            self.macro_collector = None
            logger.warning("No Alpha Vantage API key provided. Macro data collection will be skipped.")
            
        if news_api_key:
            self.news_collector = NewsSentimentCollector(news_api_key, output_dir=data_dir)
        else:
            self.news_collector = None
            logger.warning("No News API key provided. News sentiment collection will be skipped.")
        
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
    
    def run_data_collection(self, skip_market=False, skip_macro=False, skip_news=False):
        """Run the data collection phase"""
        logger.info("Starting data collection phase...")
        start_time = time.time()
        
        # Process freight data
        logger.info("Processing freight data...")
        full_route_data = [
            {"Route": "TD2", "Description": "270K Middle East Gulf to Singapore", "Worldscale": 78.00, "TCE": 60328, "Change (TCE)": 183, "OPEX": 8080},
            {"Route": "TD3C", "Description": "270K Middle East Gulf to China (VLCC)", "Worldscale": 77.15, "TCE": 57589, "Change (TCE)": 698, "OPEX": 8080},
            {"Route": "TD6", "Description": "135K Black Sea to Mediterranean (Suezmax)", "Worldscale": 90.10, "TCE": 28351, "Change (TCE)": 645, "OPEX": 7321},
            {"Route": "TD7", "Description": "80K North Sea to Continent (Aframax)", "Worldscale": 110.00, "TCE": 20317, "Change (TCE)": 1294, "OPEX": 7030},
            {"Route": "TD8", "Description": "80K Kuwait to Singapore", "Worldscale": 138.21, "TCE": 28217, "Change (TCE)": 2098, "OPEX": 7030},
            {"Route": "TD9", "Description": "70K Caribbean to US Gulf (LR1)", "Worldscale": 131.56, "TCE": 22821, "Change (TCE)": -2063, "OPEX": 6876},
            {"Route": "TD15", "Description": "260K West Africa to China (VLCC)", "Worldscale": 77.39, "TCE": 57966, "Change (TCE)": 1591, "OPEX": 8080},
            {"Route": "TD20", "Description": "130K West Africa to UK-Continent (Suezmax)", "Worldscale": 85.67, "TCE": 32492, "Change (TCE)": 125, "OPEX": 7321},
            {"Route": "TD22", "Description": "270K US Gulf to China", "Worldscale": 6820000.00, "TCE": 29834, "Change (TCE)": 2399, "OPEX": 8080},
            {"Route": "TD25", "Description": "70K US Gulf to UK-Continent", "Worldscale": 130.28, "TCE": 27378, "Change (TCE)": -1394, "OPEX": 7030},
            {"Route": "TD27", "Description": "130K Guyana to ARA", "Worldscale": 79.33, "TCE": 28226, "Change (TCE)": 162, "OPEX": 7321},
            {"Route": "TC5", "Description": "55K CPP Middle East Gulf to Japan (LR1)", "Worldscale": 172.81, "TCE": 25786, "Change (TCE)": -141, "OPEX": 6876},
            {"Route": "TC8", "Description": "65K CPP Middle East Gulf to UK-Continent (LR1)", "Worldscale": 50.33, "TCE": 30550, "Change (TCE)": -908, "OPEX": 6876},
            {"Route": "TC12", "Description": "35K Naphtha West Coast India to Japan (MR)", "Worldscale": 160.31, "TCE": 13201, "Change (TCE)": 236, "OPEX": 6876},
            {"Route": "TC15", "Description": "80K Naphtha Mediterranean to Far East (Aframax)", "Worldscale": 3094167, "TCE": 8946, "Change (TCE)": -605, "OPEX": 7030},
            {"Route": "TC16", "Description": "60K ARA to Offshore Lome (LR1)", "Worldscale": 114.72, "TCE": 17103, "Change (TCE)": 152, "OPEX": 6876},
            {"Route": "TC17", "Description": "35K CPP Jubail to Dar es Salaam (MR)", "Worldscale": 216.07, "TCE": 20319, "Change (TCE)": 777, "OPEX": 6876},
            {"Route": "TC18", "Description": "37K CPP US Gulf to Brazil (MR)", "Worldscale": 185.00, "TCE": 20728, "Change (TCE)": -2818, "OPEX": 6876},
            {"Route": "TC19", "Description": "37K CPP Amsterdam to Lagos (MR)", "Worldscale": 199.06, "TCE": 26023, "Change (TCE)": 55, "OPEX": 6876},
            {"Route": "TC20", "Description": "90K CPP Middle East Gulf to UK-Continent (Aframax)", "Worldscale": 3956250, "TCE": 36279, "Change (TCE)": 2492, "OPEX": 7030},
            # Convert tuples to dictionaries for proper handling
            {"Route": "TC21", "Description": "CPP US Gulf to Caribbean (Houston to Pozos Colorados)", "Worldscale": 185.00, "TCE": 38000, "Change (TCE)": 15, "OPEX": 6876},
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
            sentiment_analysis = self.news_collector.analyze_sentiment_distribution()
            logger.info(f"Collected news sentiment data for {len(sentiment_analysis) if sentiment_analysis is not None else 0} routes")
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
        
        # 1. Data Collection
        collection_result = self.run_data_collection(skip_market, skip_macro, skip_news)
        
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
    
    parser.add_argument("--use-local-market-data", action="store_true", 
                       help="Use local market data files instead of yfinance API")
    parser.add_argument("--skip-market", action="store_true", help="Skip market data collection")
    parser.add_argument("--skip-macro", action="store_true", help="Skip macroeconomic data collection")
    parser.add_argument("--skip-news", action="store_true", help="Skip news sentiment collection")
    parser.add_argument("--skip-ml", action="store_true", help="Skip ML pipeline")
    parser.add_argument("--alpha-vantage-key", type=str, help="Alpha Vantage API key for macro data")
    parser.add_argument("--news-api-key", type=str, help="News API key for sentiment analysis")
    parser.add_argument("--output", type=str, default="Maritime_Per_Week.pdf", help="Output report filename")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    pipeline = MaritimePipeline(
        alpha_vantage_key=args.alpha_vantage_key,
        news_api_key=args.news_api_key,
        use_local_market_data=args.use_local_market_data  # Pass the flag
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