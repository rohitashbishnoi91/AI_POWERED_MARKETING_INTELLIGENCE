"""
Report generation module for creating executive reports in multiple formats
"""

import pandas as pd
import json
import markdown
import logging
from datetime import datetime
from typing import Dict, List, Optional
from jinja2 import Template
import plotly.express as px
import plotly.graph_objects as go
import base64
from io import BytesIO

from config import *

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate executive reports in multiple formats"""
    
    def __init__(self, data: pd.DataFrame, insights: Dict):
        """Initialize the report generator"""
        self.data = data
        self.insights = insights
        self.report_date = datetime.now()
        
    def generate_full_report(self, output_dir: str = REPORTS_DIR) -> Dict[str, str]:
        """Generate complete report in multiple formats"""
        logger.info("Generating full executive report...")
        
        report_paths = {}
        
        # Generate Markdown report
        markdown_content = self._generate_markdown_report()
        markdown_path = f"{output_dir}/executive_report_{self.report_date.strftime('%Y%m%d_%H%M%S')}.md"
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        report_paths['markdown'] = markdown_path
        
        # Generate HTML report
        html_content = self._generate_html_report()
        html_path = f"{output_dir}/executive_report_{self.report_date.strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        report_paths['html'] = html_path
        
        logger.info(f"Reports generated: {list(report_paths.keys())}")
        return report_paths
    
    def _generate_markdown_report(self) -> str:
        """Generate comprehensive Markdown report"""
        
        # Calculate key metrics
        key_metrics = self._calculate_key_metrics()
        
        # Generate charts data for embedding
        charts_data = self._generate_charts_data()
        
        markdown_template = """
# {title}

**Generated on:** {date}  
**Data Period:** Market Intelligence Analysis  
**Prepared by:** {company}

---

## Executive Summary

### Key Findings

{key_findings}

### Market Size & Health
- **Total Apps Analyzed:** {total_apps:,}
- **Data Sources:** {data_sources}
- **Average Rating:** {avg_rating:.2f}/5.0
- **Market Coverage:** {categories} categories
- **Confidence Level:** {confidence_level}

---

## Market Overview

### Market Landscape
{market_assessment}

### Dominant Trends
{dominant_trends}

### Data Quality Assessment
- **Overall Confidence Score:** {overall_confidence:.2f}/1.0
- **Data Completeness:** {data_completeness:.1f}%
- **Sample Size Confidence:** {sample_confidence:.2f}/1.0
- **Source Diversity Score:** {source_diversity:.2f}/1.0

---

## Category Analysis

### Top Performing Categories
{top_categories_table}

### Category Insights
{category_insights}

### Competitive Landscape by Category
{category_competitive_analysis}

---

## User Behavior & Preferences

### Key Behavioral Patterns
{user_behavior_insights}

### Engagement Metrics
{engagement_patterns}

### Price Sensitivity Analysis
{price_sensitivity}

---

## Competitive Intelligence

### Market Leaders
{market_leaders}

### Success Factors
{success_factors}

### Competitive Gaps & Opportunities
{competitive_gaps}

---

## Strategic Opportunities & Threats

### Market Opportunities
{market_opportunities}

### Market Threats
{market_threats}

### Risk Assessment
{risk_assessment}

---

## Strategic Recommendations

### Product Strategy
{product_recommendations}

### Marketing Strategy
{marketing_recommendations}

### Competitive Strategy
{competitive_recommendations}

### Investment Priorities
{investment_priorities}

---

## Appendix

### Methodology
This analysis was conducted using AI-powered market intelligence on {total_apps:,} mobile applications from multiple data sources including Google Play Store and Apple App Store. The insights were generated using advanced language models with statistical validation and confidence scoring.

### Data Sources
{data_sources_detail}

### Confidence & Limitations
- **Analysis Confidence:** {confidence_level}
- **Data Coverage:** {data_coverage}
- **Key Limitations:** {limitations}

---

*Report generated automatically by AI-Powered Market Intelligence System*  
*© {company} - {date}*
"""

        # Format the template
        formatted_report = markdown_template.format(
            title=REPORT_TITLE,
            date=self.report_date.strftime("%B %d, %Y at %I:%M %p"),
            company=COMPANY_NAME,
            total_apps=len(self.data),
            data_sources=", ".join(self.data['data_source'].unique()) if 'data_source' in self.data.columns else "N/A",
            avg_rating=self.data['rating'].mean() if 'rating' in self.data.columns else 0,
            categories=self.data['category'].nunique() if 'category' in self.data.columns else 0,
            confidence_level=self.insights.get('confidence_scores', {}).get('confidence_level', 'Unknown'),
            overall_confidence=self.insights.get('confidence_scores', {}).get('overall_confidence', 0),
            data_completeness=self.insights.get('confidence_scores', {}).get('overall_completeness', 0) * 100,
            sample_confidence=self.insights.get('confidence_scores', {}).get('sample_size_confidence', 0),
            source_diversity=self.insights.get('confidence_scores', {}).get('source_diversity', 0),
            key_findings=self._format_list_items(self.insights.get('market_overview', {}).get('key_findings', [])),
            market_assessment=self.insights.get('market_overview', {}).get('market_size_assessment', 'Analysis pending...'),
            dominant_trends=self._format_list_items(self.insights.get('market_overview', {}).get('dominant_trends', [])),
            top_categories_table=self._generate_top_categories_table(),
            category_insights=self._format_category_insights(),
            category_competitive_analysis=self._format_competitive_by_category(),
            user_behavior_insights=self._format_list_items(self.insights.get('user_behavior_insights', {}).get('user_preferences', [])),
            engagement_patterns=self._format_list_items(self.insights.get('user_behavior_insights', {}).get('engagement_patterns', [])),
            price_sensitivity=self.insights.get('user_behavior_insights', {}).get('price_sensitivity', 'Analysis pending...'),
            market_leaders=self._format_list_items(self.insights.get('competitive_landscape', {}).get('market_leaders', [])),
            success_factors=self._format_list_items(self.insights.get('competitive_landscape', {}).get('success_factors', [])),
            competitive_gaps=self._format_list_items(self.insights.get('competitive_landscape', {}).get('competitive_gaps', [])),
            market_opportunities=self._format_opportunities(self.insights.get('opportunities_threats', {}).get('market_opportunities', [])),
            market_threats=self._format_threats(self.insights.get('opportunities_threats', {}).get('market_threats', [])),
            risk_assessment=self._generate_risk_assessment(),
            product_recommendations=self._format_recommendations(self.insights.get('recommendations', {}).get('product_strategy', [])),
            marketing_recommendations=self._format_recommendations(self.insights.get('recommendations', {}).get('marketing_strategy', [])),
            competitive_recommendations=self._format_recommendations(self.insights.get('recommendations', {}).get('competitive_strategy', [])),
            investment_priorities=self._format_list_items(self.insights.get('recommendations', {}).get('investment_priorities', [])),
            data_sources_detail=self._generate_data_sources_detail(),
            data_coverage=self._generate_data_coverage(),
            limitations=self._generate_limitations()
        )
        
        return formatted_report
    
    def _generate_html_report(self) -> str:
        """Generate interactive HTML report"""
        
        # Generate charts
        charts = self._generate_html_charts()
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #5d6d7e;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .insight-card {{
            background-color: #ecf0f1;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .opportunity {{
            border-left-color: #27ae60;
        }}
        .threat {{
            border-left-color: #e74c3c;
        }}
        .chart-container {{
            margin: 20px 0;
            padding: 15px;
            background-color: #fafafa;
            border-radius: 8px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .confidence-indicator {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .confidence-high {{ background-color: #d4edda; color: #155724; }}
        .confidence-medium {{ background-color: #fff3cd; color: #856404; }}
        .confidence-low {{ background-color: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p><strong>Generated:</strong> {date} | <strong>Company:</strong> {company}</p>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{total_apps:,}</div>
                <div class="metric-label">Total Apps Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_rating:.2f}</div>
                <div class="metric-label">Average Rating</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{categories}</div>
                <div class="metric-label">Categories</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{confidence_level}</div>
                <div class="metric-label">Confidence Level</div>
            </div>
        </div>
        
        <h2>📊 Executive Summary</h2>
        <div class="insight-card">
            <h3>Key Market Findings</h3>
            <ul>
                {key_findings_html}
            </ul>
        </div>
        
        <h2>📈 Market Overview</h2>
        {market_charts}
        
        <h2>📂 Category Analysis</h2>
        {category_table}
        {category_charts}
        
        <h2>🥊 Competitive Intelligence</h2>
        <div class="insight-card">
            <h3>Market Leaders</h3>
            <ul>
                {market_leaders_html}
            </ul>
        </div>
        
        <div class="insight-card">
            <h3>Success Factors</h3>
            <ul>
                {success_factors_html}
            </ul>
        </div>
        
        <h2>🎯 Opportunities & Threats</h2>
        <div class="insight-card opportunity">
            <h3>Market Opportunities</h3>
            <ul>
                {opportunities_html}
            </ul>
        </div>
        
        <div class="insight-card threat">
            <h3>Market Threats</h3>
            <ul>
                {threats_html}
            </ul>
        </div>
        
        <h2>💡 Strategic Recommendations</h2>
        {recommendations_html}
        
        <h2>📋 Data Quality & Confidence</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Score</th>
                <th>Level</th>
            </tr>
            <tr>
                <td>Overall Confidence</td>
                <td>{overall_confidence:.2f}/1.0</td>
                <td><span class="confidence-indicator confidence-{confidence_class}">{confidence_level}</span></td>
            </tr>
            <tr>
                <td>Data Completeness</td>
                <td>{data_completeness:.1f}%</td>
                <td><span class="confidence-indicator confidence-{completeness_class}">Good</span></td>
            </tr>
            <tr>
                <td>Sample Size</td>
                <td>{total_apps:,} apps</td>
                <td><span class="confidence-indicator confidence-high">Excellent</span></td>
            </tr>
        </table>
        
        <div class="footer">
            <p><em>Report generated automatically by AI-Powered Market Intelligence System</em></p>
            <p>© {company} - {date}</p>
        </div>
    </div>
    
    <script>
        {chart_scripts}
    </script>
</body>
</html>
"""

        # Calculate values for template
        confidence_score = self.insights.get('confidence_scores', {}).get('overall_confidence', 0)
        confidence_class = 'high' if confidence_score >= 0.8 else 'medium' if confidence_score >= 0.6 else 'low'
        completeness_score = self.insights.get('confidence_scores', {}).get('overall_completeness', 0)
        completeness_class = 'high' if completeness_score >= 0.8 else 'medium' if completeness_score >= 0.6 else 'low'
        
        formatted_html = html_template.format(
            title=REPORT_TITLE,
            date=self.report_date.strftime("%B %d, %Y at %I:%M %p"),
            company=COMPANY_NAME,
            total_apps=len(self.data),
            avg_rating=self.data['rating'].mean() if 'rating' in self.data.columns else 0,
            categories=self.data['category'].nunique() if 'category' in self.data.columns else 0,
            confidence_level=self.insights.get('confidence_scores', {}).get('confidence_level', 'Unknown'),
            overall_confidence=confidence_score,
            data_completeness=completeness_score * 100,
            confidence_class=confidence_class,
            completeness_class=completeness_class,
            key_findings_html=self._format_list_items_html(self.insights.get('market_overview', {}).get('key_findings', [])),
            market_charts=charts.get('market_overview', ''),
            category_table=self._generate_category_table_html(),
            category_charts=charts.get('category_analysis', ''),
            market_leaders_html=self._format_list_items_html(self.insights.get('competitive_landscape', {}).get('market_leaders', [])),
            success_factors_html=self._format_list_items_html(self.insights.get('competitive_landscape', {}).get('success_factors', [])),
            opportunities_html=self._format_opportunities_html(self.insights.get('opportunities_threats', {}).get('market_opportunities', [])),
            threats_html=self._format_threats_html(self.insights.get('opportunities_threats', {}).get('market_threats', [])),
            recommendations_html=self._format_recommendations_html(),
            chart_scripts=charts.get('scripts', '')
        )
        
        return formatted_html
    
    def _calculate_key_metrics(self) -> Dict:
        """Calculate key metrics for the report"""
        metrics = {
            'total_apps': len(self.data),
            'avg_rating': self.data['rating'].mean() if 'rating' in self.data.columns else 0,
            'categories': self.data['category'].nunique() if 'category' in self.data.columns else 0,
            'free_percentage': self.data['is_free'].mean() * 100 if 'is_free' in self.data.columns else 0,
            'data_sources': list(self.data['data_source'].unique()) if 'data_source' in self.data.columns else []
        }
        return metrics
    
    def _format_list_items(self, items: List) -> str:
        """Format list items for Markdown"""
        if not items:
            return "No data available."
        return "\\n".join([f"- {item}" for item in items])
    
    def _format_list_items_html(self, items: List) -> str:
        """Format list items for HTML"""
        if not items:
            return "<li>No data available.</li>"
        return "\\n".join([f"<li>{item}</li>" for item in items])
    
    def _generate_top_categories_table(self) -> str:
        """Generate top categories table for Markdown"""
        if 'category' not in self.data.columns:
            return "Category data not available."
        
        category_metrics = self.data.groupby('category').agg({
            'rating': 'mean',
            'review_count': 'mean',
            'app_name': 'count'
        }).round(2)
        category_metrics.columns = ['Avg Rating', 'Avg Reviews', 'App Count']
        top_categories = category_metrics.sort_values('App Count', ascending=False).head(10)
        
        table = "| Category | App Count | Avg Rating | Avg Reviews |\\n"
        table += "|----------|-----------|------------|-------------|\\n"
        
        for category, row in top_categories.iterrows():
            table += f"| {category} | {int(row['App Count'])} | {row['Avg Rating']:.2f} | {int(row['Avg Reviews'])} |\\n"
        
        return table
    
    def _generate_category_table_html(self) -> str:
        """Generate category table for HTML"""
        if 'category' not in self.data.columns:
            return "<p>Category data not available.</p>"
        
        category_metrics = self.data.groupby('category').agg({
            'rating': 'mean',
            'review_count': 'mean',
            'app_name': 'count'
        }).round(2)
        category_metrics.columns = ['Avg Rating', 'Avg Reviews', 'App Count']
        top_categories = category_metrics.sort_values('App Count', ascending=False).head(10)
        
        table = """
        <table>
            <tr>
                <th>Category</th>
                <th>App Count</th>
                <th>Avg Rating</th>
                <th>Avg Reviews</th>
            </tr>
        """
        
        for category, row in top_categories.iterrows():
            table += f"""
            <tr>
                <td>{category}</td>
                <td>{int(row['App Count'])}</td>
                <td>{row['Avg Rating']:.2f}</td>
                <td>{int(row['Avg Reviews']):,}</td>
            </tr>
            """
        
        table += "</table>"
        return table
    
    def _format_category_insights(self) -> str:
        """Format category insights"""
        if 'category_analysis' not in self.insights:
            return "Category analysis pending..."
        
        analysis = self.insights['category_analysis']
        insights = []
        
        if 'most_competitive_categories' in analysis:
            insights.append(f"**Most Competitive:** {', '.join(analysis['most_competitive_categories'])}")
        
        if 'underserved_categories' in analysis:
            insights.append(f"**Underserved Opportunities:** {', '.join(analysis['underserved_categories'])}")
        
        if 'highest_rated_categories' in analysis:
            insights.append(f"**Highest Quality:** {', '.join(analysis['highest_rated_categories'])}")
        
        return "\\n\\n".join(insights) if insights else "Analysis pending..."
    
    def _format_competitive_by_category(self) -> str:
        """Format competitive analysis by category"""
        if 'category' not in self.data.columns:
            return "Category data not available."
        
        # Simple competitive intensity calculation
        category_competition = self.data.groupby('category').agg({
            'app_name': 'count',
            'rating': 'mean'
        }).round(2)
        category_competition.columns = ['Apps', 'Avg Rating']
        category_competition['Competition Level'] = pd.cut(
            category_competition['Apps'], 
            bins=[0, 50, 200, 500, float('inf')], 
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        high_competition = category_competition[category_competition['Competition Level'].isin(['High', 'Very High'])]
        
        result = "**High Competition Categories:**\\n"
        for category, row in high_competition.head(5).iterrows():
            result += f"- {category}: {row['Apps']} apps (avg rating: {row['Avg Rating']:.2f})\\n"
        
        return result
    
    def _format_opportunities(self, opportunities: List) -> str:
        """Format opportunities section"""
        if not opportunities:
            return "No opportunities identified."
        
        formatted = []
        for opp in opportunities:
            if isinstance(opp, dict):
                impact = opp.get('potential_impact', 'Unknown')
                formatted.append(f"- **{opp.get('opportunity', opp)}** (Impact: {impact})")
            else:
                formatted.append(f"- {opp}")
        
        return "\\n".join(formatted)
    
    def _format_threats(self, threats: List) -> str:
        """Format threats section"""
        if not threats:
            return "No significant threats identified."
        
        formatted = []
        for threat in threats:
            if isinstance(threat, dict):
                risk = threat.get('risk_level', 'Unknown')
                formatted.append(f"- **{threat.get('threat', threat)}** (Risk: {risk})")
            else:
                formatted.append(f"- {threat}")
        
        return "\\n".join(formatted)
    
    def _format_recommendations(self, recommendations: List) -> str:
        """Format recommendations section"""
        if not recommendations:
            return "No recommendations available."
        
        formatted = []
        for rec in recommendations:
            if isinstance(rec, dict):
                priority = rec.get('priority', 'Medium')
                timeline = rec.get('timeline', 'Medium-term')
                formatted.append(f"- **{rec.get('recommendation', rec)}** (Priority: {priority}, Timeline: {timeline})")
            else:
                formatted.append(f"- {rec}")
        
        return "\\n".join(formatted)
    
    def _format_opportunities_html(self, opportunities: List) -> str:
        """Format opportunities for HTML"""
        if not opportunities:
            return "<li>No opportunities identified.</li>"
        
        formatted = []
        for opp in opportunities:
            if isinstance(opp, dict):
                impact = opp.get('potential_impact', 'Unknown')
                formatted.append(f"<li><strong>{opp.get('opportunity', opp)}</strong> <em>(Impact: {impact})</em></li>")
            else:
                formatted.append(f"<li>{opp}</li>")
        
        return "\\n".join(formatted)
    
    def _format_threats_html(self, threats: List) -> str:
        """Format threats for HTML"""
        if not threats:
            return "<li>No significant threats identified.</li>"
        
        formatted = []
        for threat in threats:
            if isinstance(threat, dict):
                risk = threat.get('risk_level', 'Unknown')
                formatted.append(f"<li><strong>{threat.get('threat', threat)}</strong> <em>(Risk: {risk})</em></li>")
            else:
                formatted.append(f"<li>{threat}</li>")
        
        return "\\n".join(formatted)
    
    def _format_recommendations_html(self) -> str:
        """Format all recommendations for HTML"""
        if 'recommendations' not in self.insights:
            return "<p>Recommendations pending...</p>"
        
        recs = self.insights['recommendations']
        html = ""
        
        for category, items in recs.items():
            if category != 'investment_priorities' and items:
                html += f"<div class='insight-card'><h3>{category.replace('_', ' ').title()}</h3><ul>"
                for item in items:
                    if isinstance(item, dict):
                        priority = item.get('priority', 'Medium')
                        timeline = item.get('timeline', 'Medium-term')
                        html += f"<li><strong>{item.get('recommendation', item)}</strong> <em>(Priority: {priority}, Timeline: {timeline})</em></li>"
                    else:
                        html += f"<li>{item}</li>"
                html += "</ul></div>"
        
        return html
    
    def _generate_html_charts(self) -> Dict[str, str]:
        """Generate HTML charts using Plotly"""
        charts = {'scripts': ''}
        
        try:
            # Category distribution chart
            if 'category' in self.data.columns:
                category_counts = self.data['category'].value_counts().head(10)
                
                chart_script = f"""
                var categoryData = {{
                    x: {list(category_counts.values)},
                    y: {list(category_counts.index)},
                    type: 'bar',
                    orientation: 'h',
                    marker: {{color: '#3498db'}}
                }};
                
                var categoryLayout = {{
                    title: 'Top 10 Categories by App Count',
                    xaxis: {{title: 'Number of Apps'}},
                    yaxis: {{title: 'Category'}},
                    height: 400
                }};
                
                Plotly.newPlot('categoryChart', [categoryData], categoryLayout);
                """
                
                charts['category_analysis'] = '<div id="categoryChart" class="chart-container"></div>'
                charts['scripts'] += chart_script
            
            # Rating distribution chart
            if 'rating' in self.data.columns:
                rating_script = f"""
                var ratingData = {{
                    x: {list(self.data['rating'].dropna())},
                    type: 'histogram',
                    nbinsx: 20,
                    marker: {{color: '#e74c3c'}}
                }};
                
                var ratingLayout = {{
                    title: 'App Rating Distribution',
                    xaxis: {{title: 'Rating'}},
                    yaxis: {{title: 'Number of Apps'}},
                    height: 300
                }};
                
                Plotly.newPlot('ratingChart', [ratingData], ratingLayout);
                """
                
                charts['market_overview'] = '<div id="ratingChart" class="chart-container"></div>'
                charts['scripts'] += rating_script
                
        except Exception as e:
            logger.warning(f"Error generating charts: {e}")
        
        return charts
    
    def _generate_charts_data(self) -> Dict:
        """Generate data for charts"""
        charts_data = {}
        
        try:
            if 'category' in self.data.columns:
                charts_data['categories'] = self.data['category'].value_counts().head(10).to_dict()
            
            if 'rating' in self.data.columns:
                charts_data['ratings'] = self.data['rating'].describe().to_dict()
            
        except Exception as e:
            logger.warning(f"Error generating chart data: {e}")
        
        return charts_data
    
    def _generate_risk_assessment(self) -> str:
        """Generate risk assessment summary"""
        confidence = self.insights.get('confidence_scores', {})
        overall_conf = confidence.get('overall_confidence', 0)
        
        if overall_conf >= 0.8:
            return "**Low Risk:** High confidence in insights based on comprehensive data coverage and quality."
        elif overall_conf >= 0.6:
            return "**Medium Risk:** Moderate confidence with some data limitations. Recommendations should be validated with additional sources."
        else:
            return "**High Risk:** Limited confidence due to data quality or coverage issues. Further analysis recommended before major decisions."
    
    def _generate_data_sources_detail(self) -> str:
        """Generate detailed data sources information"""
        if 'data_source' not in self.data.columns:
            return "Data source information not available."
        
        sources = self.data['data_source'].value_counts()
        details = []
        
        for source, count in sources.items():
            percentage = (count / len(self.data)) * 100
            details.append(f"- **{source.title()}:** {count:,} apps ({percentage:.1f}%)")
        
        return "\\n".join(details)
    
    def _generate_data_coverage(self) -> str:
        """Generate data coverage assessment"""
        coverage_items = []
        
        if 'category' in self.data.columns:
            coverage_items.append(f"{self.data['category'].nunique()} app categories")
        
        if 'data_source' in self.data.columns:
            coverage_items.append(f"{self.data['data_source'].nunique()} data sources")
        
        coverage_items.append(f"{len(self.data):,} total apps")
        
        return ", ".join(coverage_items)
    
    def _generate_limitations(self) -> str:
        """Generate analysis limitations"""
        limitations = []
        
        # Check data completeness
        if 'rating' in self.data.columns:
            missing_ratings = self.data['rating'].isnull().sum()
            if missing_ratings > 0:
                limitations.append(f"{missing_ratings:,} apps missing rating data")
        
        # Check sample size by category
        if 'category' in self.data.columns:
            small_categories = (self.data['category'].value_counts() < MIN_SAMPLE_SIZE).sum()
            if small_categories > 0:
                limitations.append(f"{small_categories} categories with limited sample size")
        
        # Data freshness
        limitations.append("Analysis based on point-in-time data snapshot")
        
        if not limitations:
            limitations.append("No significant limitations identified")
        
        return "; ".join(limitations)

def generate_executive_summary(insights: Dict) -> str:
    """Generate a concise executive summary"""
    summary_points = []
    
    # Market overview
    if 'market_overview' in insights and 'key_findings' in insights['market_overview']:
        summary_points.extend(insights['market_overview']['key_findings'][:2])
    
    # Top opportunity
    if 'opportunities_threats' in insights and 'market_opportunities' in insights['opportunities_threats']:
        opportunities = insights['opportunities_threats']['market_opportunities']
        if opportunities:
            opp = opportunities[0]
            if isinstance(opp, dict):
                summary_points.append(f"Key opportunity: {opp.get('opportunity', opp)}")
            else:
                summary_points.append(f"Key opportunity: {opp}")
    
    # Key recommendation
    if 'recommendations' in insights and 'investment_priorities' in insights['recommendations']:
        priorities = insights['recommendations']['investment_priorities']
        if priorities:
            summary_points.append(f"Priority focus: {priorities[0]}")
    
    return summary_points

if __name__ == "__main__":
    # Example usage
    print("Report generator module ready!")
