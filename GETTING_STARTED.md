# 🚀 Getting Started with AI-Powered Market Intelligence

## Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
python setup.py
```

### 2. Configure API Keys
Edit the `.env` file that was created:
```env
GEMINI_API_KEY=your_gemini_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here  # Optional
```

**Get your Gemini API key**: [Google AI Studio](https://aistudio.google.com/app/apikey) (Free)

### 3. Run Demo Mode
```bash
python main.py demo
```
This will:
- Generate sample data
- Run the full AI analysis pipeline  
- Launch the interactive interface

## Using Your Own Data

### 1. Download Kaggle Dataset
Download the [Google Play Store Apps dataset](https://www.kaggle.com/datasets/lava18/google-play-store-apps) and place it in `data/raw/googleplaystore.csv`

### 2. Run Full Pipeline
```bash
python main.py pipeline --data data/raw/googleplaystore.csv
```

### 3. Launch Interface
```bash
python main.py interface --interface streamlit
```

## What You'll Get

### 📊 Interactive Dashboard
- Market overview with key metrics
- Category performance analysis
- Competitive intelligence
- AI-generated insights
- Natural language query interface

### 📋 Executive Reports
- Professional Markdown report
- Interactive HTML report with charts
- AI-powered insights and recommendations
- Confidence scoring for all analysis

### 🤖 AI-Powered Insights
- Market opportunities and threats
- User behavior analysis
- Competitive landscape assessment
- Strategic recommendations
- Category-specific insights

## Phase 5: D2C Analysis

For D2C eCommerce funnel analysis:

```python
from src.d2c_analyzer import D2CFunnelAnalyzer

# Initialize analyzer
analyzer = D2CFunnelAnalyzer('your_d2c_data.xlsx')

# Run analysis
funnel_insights = analyzer.analyze_conversion_funnel()
seo_opportunities = analyzer.analyze_seo_opportunities()
creative_content = analyzer.generate_creative_content()

# Get comprehensive report
full_report = analyzer.generate_comprehensive_report()
```

## Troubleshooting

### Common Issues

**Missing API Key Error**
```bash
# Add your Gemini API key to .env file
GEMINI_API_KEY=your_actual_key_here
```

**Data Loading Error**
```bash
# Make sure your CSV file is in the correct location
# Or run demo mode to test with sample data
python main.py demo
```

**Memory Issues**
```bash
# Reduce the number of App Store API calls
python main.py pipeline --max-apps 25
```

## Command Reference

| Command | Description |
|---------|-------------|
| `python main.py pipeline` | Run complete data pipeline |
| `python main.py interface` | Launch query interface |
| `python main.py demo` | Run with sample data |
| `python setup.py` | Initial setup |
| `streamlit run streamlit_app.py` | Direct Streamlit launch |

## Next Steps

1. **Explore the Interface**: Try different queries and filters
2. **Review Reports**: Check the `reports/` folder for generated analysis
3. **Customize Insights**: Modify prompts in `src/ai_insights.py`
4. **Add Data Sources**: Extend `src/data_pipeline.py`
5. **Phase 5 Extension**: Implement D2C funnel analysis

## Support

- Check the full [README.md](README.md) for detailed documentation
- Review code comments for implementation details
- Modify configuration in `config.py` as needed

**Happy analyzing! 🚀**
