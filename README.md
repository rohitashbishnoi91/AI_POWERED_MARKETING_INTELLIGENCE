# 🚀 AI-Powered Market Intelligence System

An advanced market intelligence system that ingests data from multiple sources, generates AI-powered insights using Gemini 2.0 Flash, and provides actionable outputs for strategic decision making.

## 🎯 Project Overview

This system was built as part of an Applied AI Engineer assignment to demonstrate capabilities in:
- **Data Pipeline Development**: Clean, robust data ingestion and processing
- **LLM Integration**: Advanced AI insights using Google's Gemini 2.0 Flash
- **Market Intelligence**: Actionable business insights with confidence scoring
- **Interactive Interfaces**: CLI and web-based query systems
- **Automated Reporting**: Professional reports in multiple formats

## 🏗️ Architecture

```
📦 AI-Powered Market Intelligence
├── 📁 src/                          # Core modules
│   ├── data_pipeline.py             # Data ingestion & cleaning
│   ├── ai_insights.py               # AI-powered analysis
│   ├── query_interface.py           # Interactive interfaces
│   └── report_generator.py          # Report generation
├── 📁 data/                         # Data storage
│   ├── raw/                         # Original datasets
│   └── processed/                   # Cleaned datasets
├── 📁 reports/                      # Generated reports
├── 📁 outputs/                      # AI insights & analysis
├── main.py                          # Main application runner
├── config.py                        # Configuration settings
└── requirements.txt                 # Dependencies
```

## 🔧 Setup & Installation

### 1. Clone and Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the root directory:

```env
# Required for AI insights
GEMINI_API_KEY=your_gemini_api_key_here

# Optional for App Store data
RAPIDAPI_KEY=your_rapidapi_key_here
```

**Getting API Keys:**
- **Gemini API**: Get free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **RapidAPI**: Sign up at [RapidAPI](https://rapidapi.com/) and subscribe to [App Store Scraper API](https://rapidapi.com/apidojo/api/app-store-scraper)

### 3. Prepare Data

**Option A: Use Your Kaggle Dataset**
1. Download the Google Play Store Apps dataset from Kaggle
2. Place it in `data/raw/googleplaystore.csv`

**Option B: Use Demo Mode**
- The system can generate sample data for demonstration

## 🚀 Quick Start

### Run Complete Pipeline

```bash
# With your own data
python main.py pipeline --data data/raw/googleplaystore.csv

# Demo mode with sample data
python main.py demo
```

### Launch Interactive Interface

```bash
# Web interface (Streamlit)
python main.py interface --interface streamlit

# Command line interface
python main.py interface --interface cli
```

## 📊 Features & Capabilities

### 🔄 Data Pipeline
- **Multi-source ingestion**: Kaggle datasets + RapidAPI
- **Intelligent cleaning**: Handle missing values, duplicates, format inconsistencies
- **Data validation**: Statistical checks and quality scoring
- **Unified schema**: Consistent data structure across sources

### 🤖 AI-Powered Analysis
- **Market Overview**: Comprehensive market assessment
- **Category Analysis**: Performance by app categories
- **Competitive Intelligence**: Market leaders and success factors
- **User Behavior Insights**: Engagement patterns and preferences
- **Opportunities & Threats**: Strategic analysis with risk assessment
- **Confidence Scoring**: Statistical validation of insights

### 📈 Interactive Query Interface

**Streamlit Web App Features:**
- 📊 Executive dashboard with key metrics
- 🔍 Interactive data explorer with filters
- 🤖 AI insights visualization
- 📂 Category performance analysis
- 🥊 Competitive intelligence
- 💬 Natural language query assistant

**CLI Features:**
- Quick market overview
- Category analysis
- Top app rankings
- Custom queries

### 📋 Automated Reporting

**Generated Reports:**
- **Markdown**: Technical documentation format
- **HTML**: Interactive web report with charts
- **Executive Summary**: Key findings and recommendations

**Report Sections:**
- Executive Summary with KPIs
- Market Overview & Trends
- Category Performance Analysis
- Competitive Landscape
- User Behavior Insights
- Strategic Opportunities
- Risk Assessment
- Actionable Recommendations

## 🎮 Usage Examples

### Example 1: Complete Analysis Pipeline

```bash
# Run full pipeline with real data
python main.py pipeline --data data/raw/googleplaystore.csv --max-apps 100

# Output:
# ✅ Pipeline completed successfully!
# 📁 Check the 'reports' folder for reports
# 📊 Check the 'outputs' folder for insights
# 💾 Check the 'data/processed' folder for processed data
```

### Example 2: Quick Demo

```bash
# Generate sample data and run analysis
python main.py demo

# Automatically launches interactive interface after completion
```

### Example 3: Query Interface

```bash
# Launch web interface
streamlit run src/query_interface.py

# Or via main application
python main.py interface --interface streamlit
```

## 📁 Output Files

After running the pipeline, you'll get:

```
📦 Generated Outputs
├── 📁 data/processed/
│   └── unified_market_data_20240101_120000.csv
├── 📁 outputs/
│   └── market_insights_20240101_120000.json
└── 📁 reports/
    ├── executive_report_20240101_120000.md
    └── executive_report_20240101_120000.html
```

## 🔍 Key Insights Generated

### Market Intelligence
- Market size and health indicators
- Category performance rankings
- Competitive landscape analysis
- User behavior patterns
- Pricing strategy insights

### Strategic Recommendations
- Product development opportunities
- Market entry strategies
- Competitive positioning
- Investment priorities
- Risk mitigation strategies

### Confidence Scoring
- Data quality assessment
- Statistical significance testing
- Source diversity evaluation
- Sample size validation

## 🎯 Phase 5 Extension: D2C Funnel Analysis

For D2C eCommerce data analysis:

```python
# Extension for D2C funnel analysis
from src.d2c_analyzer import D2CFunnelAnalyzer, SEOAnalyzer

# Load D2C data
analyzer = D2CFunnelAnalyzer('data/d2c_dataset.xlsx')

# Generate funnel insights
funnel_insights = analyzer.analyze_conversion_funnel()
seo_opportunities = analyzer.analyze_seo_opportunities()

# AI-powered creative generation
creative_outputs = analyzer.generate_creative_content()
```

## 🛠️ Customization & Extension

### Adding New Data Sources

```python
# Extend the DataPipeline class
class CustomDataPipeline(DataPipeline):
    def load_custom_data(self, source_config):
        # Implement custom data loading
        pass
```

### Custom AI Prompts

```python
# Modify prompts in ai_insights.py
def _generate_custom_insights(self, data_summary):
    custom_prompt = """
    Analyze the data for specific industry insights...
    """
    return self._query_gemini(custom_prompt, "custom_analysis")
```

### New Report Formats

```python
# Extend ReportGenerator for new formats
def generate_powerpoint_report(self):
    # Implementation for PowerPoint generation
    pass
```

## 📊 Performance & Scalability

- **Data Processing**: Handles 10K+ apps efficiently
- **API Rate Limiting**: Built-in retry logic and delays
- **Memory Management**: Chunked processing for large datasets
- **Caching**: Results caching for faster re-runs
- **Error Handling**: Graceful degradation and recovery

## 🔧 Troubleshooting

### Common Issues

**1. API Key Errors**
```bash
# Error: No Gemini API key found
# Solution: Add GEMINI_API_KEY to .env file
```

**2. Data Loading Issues**
```bash
# Error: Could not read file with any supported encoding
# Solution: Check file path and encoding (UTF-8, Latin-1 supported)
```

**3. Memory Issues with Large Datasets**
```bash
# Solution: Reduce max-apps parameter
python main.py pipeline --max-apps 25
```

### Debug Mode

```bash
# Enable detailed logging
export PYTHONPATH="${PYTHONPATH}:."
python -m logging.basicConfig level=DEBUG main.py pipeline
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is part of an Applied AI Engineer assignment. Please respect any applicable licensing terms.

## 🙏 Acknowledgments

- **Google Gemini**: For advanced AI capabilities
- **RapidAPI**: For App Store data access
- **Kaggle**: For the Google Play Store dataset
- **Streamlit**: For rapid interface development
- **Plotly**: For interactive visualizations

---

**Built with ❤️ for next-generation market intelligence**

*For questions or support, please refer to the documentation or create an issue.*
