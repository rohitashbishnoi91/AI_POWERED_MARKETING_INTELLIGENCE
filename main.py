"""
Main application runner for AI-Powered Market Intelligence System
"""

import pandas as pd
import json
import os
import argparse
import logging
from datetime import datetime

# Import our modules
from src.data_pipeline import DataPipeline, AppStoreAPI, create_unified_schema
from src.ai_insights import AIInsightsGenerator, save_insights_to_json
from src.report_generator import ReportGenerator
from src.query_interface import QueryInterface, CLIInterface
from config import *

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketIntelligenceSystem:
    """Main system coordinator"""
    
    def __init__(self):
        """Initialize the market intelligence system"""
        self.pipeline = DataPipeline()
        self.ai_generator = None
        self.appstore_api = None
        self.unified_data = None
        self.insights = None
        
        # Initialize AI generator if API key is available
        if GEMINI_API_KEY:
            self.ai_generator = AIInsightsGenerator(GEMINI_API_KEY)
            logger.info("AI insights generator initialized")
        else:
            logger.warning("No Gemini API key found. AI insights will not be available.")
        
        # Initialize App Store API if key is available
        if RAPIDAPI_KEY:
            self.appstore_api = AppStoreAPI(RAPIDAPI_KEY)
            logger.info("App Store API initialized")
        else:
            logger.warning("No RapidAPI key found. App Store data will not be available.")
    
    def run_full_pipeline(self, kaggle_data_path: str, max_appstore_apps: int = 50):
        """Run the complete data pipeline and analysis"""
        logger.info("🚀 Starting AI-Powered Market Intelligence Pipeline")
        
        try:
            # Phase 1: Data Ingestion and Cleaning
            logger.info("📥 Phase 1: Data Ingestion and Cleaning")
            self._run_data_pipeline(kaggle_data_path, max_appstore_apps)
            
            # Phase 2: AI Insights Generation
            if self.ai_generator:
                logger.info("🤖 Phase 2: AI Insights Generation")
                self._generate_insights()
            else:
                logger.warning("Skipping AI insights generation - no API key")
            
            # Phase 3: Report Generation
            logger.info("📊 Phase 3: Report Generation")
            self._generate_reports()
            
            # Phase 4: Save Results
            logger.info("💾 Phase 4: Saving Results")
            self._save_results()
            
            logger.info("✅ Pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return False
    
    def _run_data_pipeline(self, kaggle_data_path: str, max_appstore_apps: int):
        """Run data ingestion and processing"""
        
        # Load and clean Kaggle data
        if os.path.exists(kaggle_data_path):
            logger.info(f"Loading Kaggle data from {kaggle_data_path}")
            self.pipeline.load_kaggle_data(kaggle_data_path)
            kaggle_cleaned = self.pipeline.clean_kaggle_data()
            logger.info(f"Cleaned Kaggle data: {len(kaggle_cleaned)} apps")
        else:
            logger.error(f"Kaggle data file not found: {kaggle_data_path}")
            kaggle_cleaned = pd.DataFrame()
        
        # Fetch App Store data if API is available
        appstore_data = []
        if self.appstore_api and not kaggle_cleaned.empty:
            logger.info(f"Fetching App Store data (max {max_appstore_apps} apps)")
            
            # Use search queries to get diverse app data
            search_terms = ["productivity", "games", "social", "finance", "health"]
            
            for term in search_terms:
                try:
                    search_results = self.appstore_api.search_apps(term, limit=max_appstore_apps // len(search_terms))
                    appstore_data.extend(search_results)
                except Exception as e:
                    logger.warning(f"Failed to search for {term}: {e}")
                    continue
            
            logger.info(f"Fetched {len(appstore_data)} apps from App Store")
        else:
            logger.info("Skipping App Store data - API not available or no Kaggle data")
        
        # Create unified schema
        self.unified_data = create_unified_schema(kaggle_cleaned, appstore_data)
        logger.info(f"Created unified dataset with {len(self.unified_data)} apps")
    
    def _generate_insights(self):
        """Generate AI-powered insights"""
        if self.unified_data is None or self.unified_data.empty:
            logger.error("No data available for insights generation")
            return
        
        logger.info("Generating AI insights...")
        self.insights = self.ai_generator.generate_market_insights(self.unified_data)
        logger.info("AI insights generated successfully")
    
    def _generate_reports(self):
        """Generate executive reports"""
        if self.unified_data is None or self.unified_data.empty:
            logger.error("No data available for report generation")
            return
        
        # Ensure reports directory exists
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
        # Use empty insights if AI generation failed
        insights = self.insights if self.insights else {}
        
        report_generator = ReportGenerator(self.unified_data, insights)
        report_paths = report_generator.generate_full_report()
        
        logger.info(f"Reports generated: {list(report_paths.values())}")
        return report_paths
    
    def _save_results(self):
        """Save processed data and insights"""
        # Ensure output directories exist
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        
        # Save unified data
        if self.unified_data is not None:
            data_path = f"{PROCESSED_DATA_DIR}/unified_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self.unified_data.to_csv(data_path, index=False)
            logger.info(f"Unified data saved: {data_path}")
        
        # Save insights
        if self.insights:
            insights_path = f"{OUTPUTS_DIR}/market_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_insights_to_json(self.insights, insights_path)
            logger.info(f"Insights saved: {insights_path}")
    
    def launch_query_interface(self, interface_type: str = "streamlit"):
        """Launch the query interface"""
        # Find the most recent data and insights files
        data_files = [f for f in os.listdir(PROCESSED_DATA_DIR) if f.endswith('.csv')]
        insights_files = [f for f in os.listdir(OUTPUTS_DIR) if f.endswith('.json')]
        
        if not data_files:
            logger.error("No processed data files found. Run the pipeline first.")
            return
        
        data_path = os.path.join(PROCESSED_DATA_DIR, sorted(data_files)[-1])
        insights_path = os.path.join(OUTPUTS_DIR, sorted(insights_files)[-1]) if insights_files else None
        
        if interface_type.lower() == "streamlit":
            logger.info("Launching Streamlit interface...")
            logger.info("Use this command to launch Streamlit:")
            logger.info(f"python -m streamlit run streamlit_app.py")
            print(f"\\n🚀 To launch the web interface, run:")
            print(f"python -m streamlit run streamlit_app.py")
            print(f"\\nOr run the CLI interface with:")
            print(f"python main.py interface --interface cli")
        
        elif interface_type.lower() == "cli":
            logger.info("Launching CLI interface...")
            cli_interface = CLIInterface(data_path, insights_path or "")
            cli_interface.run()
        
        else:
            logger.error(f"Unknown interface type: {interface_type}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI-Powered Market Intelligence System")
    parser.add_argument("command", choices=["pipeline", "interface", "demo"], 
                       help="Command to run")
    parser.add_argument("--data", default="data/raw/googleplaystore.csv",
                       help="Path to Kaggle dataset")
    parser.add_argument("--interface", choices=["streamlit", "cli"], default="streamlit",
                       help="Interface type to launch")
    parser.add_argument("--max-apps", type=int, default=50,
                       help="Maximum apps to fetch from App Store API")
    
    args = parser.parse_args()
    
    # Initialize system
    system = MarketIntelligenceSystem()
    
    if args.command == "pipeline":
        # Run the full data pipeline
        logger.info("Running full pipeline...")
        success = system.run_full_pipeline(args.data, args.max_apps)
        if success:
            print("\\n✅ Pipeline completed successfully!")
            print(f"📁 Check the '{REPORTS_DIR}' folder for reports")
            print(f"📊 Check the '{OUTPUTS_DIR}' folder for insights")
            print(f"💾 Check the '{PROCESSED_DATA_DIR}' folder for processed data")
        else:
            print("\\n❌ Pipeline failed. Check logs for details.")
    
    elif args.command == "interface":
        # Launch query interface
        system.launch_query_interface(args.interface)
    
    elif args.command == "demo":
        # Run a quick demo with sample data
        logger.info("Running demo mode...")
        
        # Create sample data if no real data exists
        if not os.path.exists(args.data):
            logger.info("Creating sample data for demo...")
            sample_data = create_sample_data()
            os.makedirs(os.path.dirname(args.data), exist_ok=True)
            sample_data.to_csv(args.data, index=False)
            logger.info(f"Sample data created: {args.data}")
        
        # Run pipeline with limited App Store calls
        success = system.run_full_pipeline(args.data, max_appstore_apps=10)
        
        if success:
            print("\\n🎉 Demo completed! Launching interface...")
            system.launch_query_interface(args.interface)

def create_sample_data() -> pd.DataFrame:
    """Create sample data for demonstration"""
    import random
    
    logger.info("Creating sample market data...")
    
    categories = ["COMMUNICATION", "PRODUCTIVITY", "GAME", "SOCIAL", "FINANCE", 
                 "HEALTH_AND_FITNESS", "EDUCATION", "ENTERTAINMENT", "SHOPPING", "TRAVEL"]
    
    content_ratings = ["Everyone", "Teen", "Mature 17+", "Everyone 10+"]
    
    sample_size = 1000
    
    data = {
        'app': [f"Sample App {i}" for i in range(1, sample_size + 1)],
        'category': [random.choice(categories) for _ in range(sample_size)],
        'rating': [round(random.uniform(1.0, 5.0), 1) for _ in range(sample_size)],
        'reviews': [random.randint(10, 100000) for _ in range(sample_size)],
        'size': [f"{random.randint(1, 100)}M" for _ in range(sample_size)],
        'installs': [f"{random.choice(['100+', '1,000+', '10,000+', '100,000+', '1,000,000+'])}" for _ in range(sample_size)],
        'type': [random.choice(['Free', 'Paid']) for _ in range(sample_size)],
        'price': [f"${random.randint(1, 10)}.99" if random.random() > 0.7 else "0" for _ in range(sample_size)],
        'content_rating': [random.choice(content_ratings) for _ in range(sample_size)],
        'genres': [random.choice(categories) for _ in range(sample_size)],
        'last_updated': ['July 1, 2023' for _ in range(sample_size)],
        'current_ver': ['1.0' for _ in range(sample_size)],
        'android_ver': ['4.1 and up' for _ in range(sample_size)]
    }
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("🚀 AI-Powered Market Intelligence System")
    print("=" * 50)
    print("Usage examples:")
    print("  python main.py pipeline --data data/raw/googleplaystore.csv")
    print("  python main.py interface --interface streamlit")
    print("  python main.py demo")
    print("\\nFor help: python main.py --help")
    print("=" * 50)
    
    # If no arguments provided, show help
    import sys
    if len(sys.argv) == 1:
        print("\\nNo command provided. Use --help for usage information.")
    else:
        main()
