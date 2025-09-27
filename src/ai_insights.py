"""
AI-powered insights generation using Gemini API
"""

import google.generativeai as genai
import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
from scipy import stats

from config import *

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIInsightsGenerator:
    """Generate market intelligence insights using Gemini AI"""
    
    def __init__(self, api_key: str):
        """Initialize the AI insights generator"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
    def generate_market_insights(self, data: pd.DataFrame) -> Dict:
        """Generate comprehensive market insights from the combined dataset"""
        logger.info("Generating AI-powered market insights...")
        
        # Prepare data summary for AI analysis
        data_summary = self._prepare_data_summary(data)
        
        # Generate different types of insights
        insights = {
            'market_overview': self._generate_market_overview(data_summary),
            'category_analysis': self._generate_category_analysis(data, data_summary),
            'competitive_landscape': self._generate_competitive_analysis(data, data_summary),
            'user_behavior_insights': self._generate_user_behavior_insights(data, data_summary),
            'opportunities_threats': self._generate_opportunities_threats(data, data_summary),
            'recommendations': self._generate_recommendations(data, data_summary),
            'confidence_scores': self._calculate_confidence_scores(data),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_size': len(data),
                'data_sources': data['data_source'].value_counts().to_dict(),
                'model_used': GEMINI_MODEL
            }
        }
        
        return insights
    
    def _prepare_data_summary(self, data: pd.DataFrame) -> Dict:
        """Prepare a statistical summary of the data for AI analysis"""
        summary = {
            'total_apps': len(data),
            'data_sources': data['data_source'].value_counts().to_dict(),
            'category_distribution': data['category'].value_counts().head(10).to_dict(),
            'rating_stats': {
                'mean': float(data['rating'].mean()) if data['rating'].notna().any() else None,
                'median': float(data['rating'].median()) if data['rating'].notna().any() else None,
                'std': float(data['rating'].std()) if data['rating'].notna().any() else None
            },
            'pricing_stats': {
                'free_apps_percentage': float(data['is_free'].mean() * 100) if 'is_free' in data.columns else None,
                'avg_paid_app_price': float(data[data['price_usd'] > 0]['price_usd'].mean()) if 'price_usd' in data.columns else None,
                'price_range': [float(data['price_usd'].min()), float(data['price_usd'].max())] if 'price_usd' in data.columns else None
            },
            'review_stats': {
                'avg_review_count': float(data['review_count'].mean()) if 'review_count' in data.columns else None,
                'median_review_count': float(data['review_count'].median()) if 'review_count' in data.columns else None,
                'high_review_apps': int((data['review_count'] > 10000).sum()) if 'review_count' in data.columns else None
            }
        }
        
        return summary
    
    def _generate_market_overview(self, data_summary: Dict) -> Dict:
        """Generate market overview insights"""
        # Format the rating safely
        avg_rating = data_summary['rating_stats']['mean']
        avg_rating_str = f"{avg_rating:.2f}" if avg_rating is not None else "N/A"
        
        free_pct = data_summary['pricing_stats']['free_apps_percentage']
        free_pct_str = f"{free_pct:.1f}%" if free_pct is not None else "N/A"
        
        prompt = f"""
        You are a senior market intelligence analyst for a leading marketing company. Analyze the mobile app market data below and provide strategic insights.
        
        CONTEXT:
        Dataset: {data_summary['total_apps']} mobile applications
        Sources: {data_summary['data_sources']}
        Market Coverage: {list(data_summary['category_distribution'].keys())[:5]} (top categories)
        Quality Baseline: {avg_rating_str}/5.0 average rating
        Business Model Split: {free_pct_str} free apps
        
        ANALYSIS FRAMEWORK:
        1. Market Size & Opportunity Assessment
        2. Competitive Landscape Analysis  
        3. User Behavior & Preference Trends
        4. Strategic Recommendations
        
        EXAMPLE OUTPUT FORMAT:
        {{
            "key_findings": [
                "Market shows high saturation in [category] with [X] apps competing",
                "Quality gap identified: average rating of [X] suggests improvement opportunities",
                "Monetization trends: [X]% free apps indicate strong freemium adoption"
            ],
            "market_size_assessment": "Detailed assessment with specific numbers and growth indicators",
            "dominant_trends": [
                "Category trend with supporting data",
                "User behavior pattern with implications"
            ],
            "market_health_indicators": "Overall market health with specific metrics and outlook"
        }}
        
        REQUIREMENTS:
        - Use specific data points from the analysis
        - Provide actionable insights for marketing strategy
        - Include confidence indicators where relevant
        - Focus on business implications and opportunities
        
        Analyze the data and provide insights in the exact JSON format above:
        """
        
        return self._query_gemini(prompt, "market_overview")
    
    def _generate_category_analysis(self, data: pd.DataFrame, data_summary: Dict) -> Dict:
        """Generate category-specific insights"""
        # Calculate category performance metrics
        category_metrics = data.groupby('category').agg({
            'rating': ['mean', 'count'],
            'review_count': 'mean',
            'price_usd': 'mean',
            'is_free': 'mean'
        }).round(2)
        
        category_metrics.columns = ['avg_rating', 'app_count', 'avg_reviews', 'avg_price', 'free_percentage']
        top_categories = category_metrics.nlargest(10, 'app_count')
        
        prompt = f"""
        Analyze the mobile app category performance data:
        
        Top 10 Categories by App Count:
        {top_categories.to_string()}
        
        Provide category insights in JSON format:
        {{
            "most_competitive_categories": ["category1", "category2"],
            "underserved_categories": ["category1", "category2"],
            "highest_rated_categories": ["category1", "category2"],
            "monetization_opportunities": ["insight1", "insight2"],
            "category_trends": {{"category": "trend_description"}}
        }}
        
        Focus on opportunities for app developers and marketers.
        """
        
        return self._query_gemini(prompt, "category_analysis")
    
    def _generate_competitive_analysis(self, data: pd.DataFrame, data_summary: Dict) -> Dict:
        """Generate competitive landscape insights"""
        # Identify top performers  
        # Convert review_count to numeric if needed
        if 'review_count' in data.columns:
            data['review_count'] = pd.to_numeric(data['review_count'], errors='coerce').fillna(0)
        
        top_rated = data.nlargest(10, 'rating')[['app_name', 'category', 'rating', 'review_count']]
        most_reviewed = data.nlargest(10, 'review_count')[['app_name', 'category', 'rating', 'review_count']]
        
        prompt = f"""
        Analyze the competitive landscape based on app performance data:
        
        Top 10 Highest Rated Apps:
        {top_rated.to_string()}
        
        Top 10 Most Reviewed Apps:
        {most_reviewed.to_string()}
        
        Provide competitive insights in JSON format:
        {{
            "market_leaders": ["app/company1", "app/company2"],
            "success_factors": ["factor1", "factor2", "factor3"],
            "competitive_gaps": ["gap1", "gap2"],
            "emerging_competitors": ["insight1", "insight2"],
            "market_entry_barriers": ["barrier1", "barrier2"]
        }}
        
        Focus on strategic insights for market positioning.
        """
        
        return self._query_gemini(prompt, "competitive_analysis")
    
    def _generate_user_behavior_insights(self, data: pd.DataFrame, data_summary: Dict) -> Dict:
        """Generate user behavior and preference insights"""
        # Analyze rating vs review count correlation
        rating_review_corr = data['rating'].corr(data['review_count']) if data['rating'].notna().any() and data['review_count'].notna().any() else None
        corr_str = f"{rating_review_corr:.3f}" if rating_review_corr is not None else "N/A"
        
        # Format rating and percentage safely
        avg_rating = data_summary['rating_stats']['mean']
        avg_rating_str = f"{avg_rating:.2f}" if avg_rating is not None else "N/A"
        
        free_pct = data_summary['pricing_stats']['free_apps_percentage']
        free_pct_str = f"{free_pct:.1f}%" if free_pct is not None else "N/A"
        
        # Price sensitivity analysis
        if 'price_usd' in data.columns:
            price_segments = data.groupby(pd.cut(data['price_usd'], bins=[0, 0.99, 4.99, 9.99, float('inf')], labels=['Free', 'Low($1-5)', 'Medium($5-10)', 'High($10+)']))['rating'].mean()
        else:
            price_segments = None
        
        prompt = f"""
        Analyze user behavior patterns from app data:
        
        Key Metrics:
        - Rating-Review correlation: {corr_str}
        - Average rating: {avg_rating_str}
        - Free apps preference: {free_pct_str}
        
        Price vs Rating Analysis:
        {price_segments.to_string() if price_segments is not None else 'N/A'}
        
        Provide user behavior insights in JSON format:
        {{
            "user_preferences": ["preference1", "preference2"],
            "engagement_patterns": ["pattern1", "pattern2"],
            "price_sensitivity": "analysis",
            "rating_behaviors": ["behavior1", "behavior2"],
            "adoption_factors": ["factor1", "factor2"]
        }}
        
        Focus on insights for user acquisition and retention strategies.
        """
        
        return self._query_gemini(prompt, "user_behavior")
    
    def _generate_opportunities_threats(self, data: pd.DataFrame, data_summary: Dict) -> Dict:
        """Generate market opportunities and threats analysis"""
        # Format safely
        avg_rating = data_summary['rating_stats']['mean']
        avg_rating_str = f"{avg_rating:.2f}" if avg_rating is not None else "N/A"
        
        free_pct = data_summary['pricing_stats']['free_apps_percentage']
        free_pct_str = f"{free_pct:.1f}" if free_pct is not None else "N/A"
        
        prompt = f"""
        Based on the mobile app market analysis, identify opportunities and threats:
        
        Market Context:
        - Total market size: {data_summary['total_apps']} apps analyzed
        - Market fragmentation: {len(data_summary['category_distribution'])} categories
        - Competition level: Average {avg_rating_str} rating
        - Monetization: {free_pct_str}% free apps
        
        Provide opportunities and threats in JSON format:
        {{
            "market_opportunities": [
                {{"opportunity": "description", "potential_impact": "high/medium/low"}},
                {{"opportunity": "description", "potential_impact": "high/medium/low"}}
            ],
            "market_threats": [
                {{"threat": "description", "risk_level": "high/medium/low"}},
                {{"threat": "description", "risk_level": "high/medium/low"}}
            ],
            "strategic_recommendations": ["recommendation1", "recommendation2"]
        }}
        
        Focus on actionable insights for business strategy.
        """
        
        return self._query_gemini(prompt, "opportunities_threats")
    
    def _generate_recommendations(self, data: pd.DataFrame, data_summary: Dict) -> Dict:
        """Generate strategic recommendations"""
        # Format safely
        avg_rating = data_summary['rating_stats']['mean']
        avg_rating_str = f"{avg_rating:.2f}" if avg_rating is not None else "N/A"
        
        free_pct = data_summary['pricing_stats']['free_apps_percentage']
        free_pct_str = f"{free_pct:.1f}" if free_pct is not None else "N/A"
        
        prompt = f"""
        You are a strategic consultant providing recommendations to a marketing technology company based on comprehensive market analysis.
        
        MARKET INTELLIGENCE SUMMARY:
        Total Market Size: {data_summary['total_apps']} applications analyzed
        Key Categories: {list(data_summary['category_distribution'].keys())[:5]}
        Market Quality: {avg_rating_str}/5.0 average rating
        Business Models: {free_pct_str}% freemium adoption
        
        STRATEGIC CONTEXT:
        - Company: Marketing technology firm seeking growth opportunities
        - Objective: Identify actionable strategies for market entry/expansion
        - Timeline: Need both immediate wins and long-term positioning
        
        EXAMPLE RECOMMENDATION FORMAT:
        {{
            "product_strategy": [
                {{
                    "recommendation": "Develop AI-powered app analytics tool targeting underserved categories",
                    "priority": "high",
                    "timeline": "short-term",
                    "rationale": "Market gap identified in [specific area] with [supporting data]"
                }}
            ],
            "marketing_strategy": [
                {{
                    "recommendation": "Focus marketing efforts on high-growth categories with quality gaps",
                    "priority": "medium", 
                    "timeline": "medium-term",
                    "rationale": "[Category] shows [X]% growth but [Y] average rating indicates opportunity"
                }}
            ],
            "competitive_strategy": [
                {{
                    "recommendation": "Differentiate through superior user experience in saturated markets",
                    "priority": "high",
                    "timeline": "long-term",
                    "rationale": "Market leaders have [specific weakness] creating differentiation opportunity"
                }}
            ],
            "investment_priorities": [
                "AI/ML capabilities for personalization",
                "User experience optimization tools", 
                "Market analytics platform development"
            ]
        }}
        
        REQUIREMENTS:
        - Base all recommendations on specific data insights
        - Provide clear rationale for each recommendation
        - Ensure recommendations are implementable and specific
        - Prioritize based on market opportunity size and feasibility
        
        Provide strategic recommendations in the exact JSON format above:
        """
        
        return self._query_gemini(prompt, "recommendations")
    
    def _calculate_confidence_scores(self, data: pd.DataFrame) -> Dict:
        """Calculate confidence scores for insights based on data quality"""
        scores = {}
        
        # Data completeness score
        completeness = {}
        key_fields = ['app_name', 'category', 'rating', 'review_count']
        for field in key_fields:
            if field in data.columns:
                completeness[field] = float(1 - data[field].isnull().mean())
        
        scores['data_completeness'] = completeness
        scores['overall_completeness'] = float(np.mean(list(completeness.values())))
        
        # Sample size confidence
        scores['sample_size_confidence'] = min(1.0, len(data) / 1000)  # Confidence increases with sample size
        
        # Data source diversity
        source_diversity = len(data['data_source'].unique()) if 'data_source' in data.columns else 1
        scores['source_diversity'] = min(1.0, source_diversity / 2)  # Max confidence with 2+ sources
        
        # Statistical significance for categorical insights
        category_counts = data['category'].value_counts() if 'category' in data.columns else pd.Series()
        scores['category_significance'] = float((category_counts >= MIN_SAMPLE_SIZE).mean())
        
        # Overall confidence score
        weights = {
            'overall_completeness': 0.3,
            'sample_size_confidence': 0.3,
            'source_diversity': 0.2,
            'category_significance': 0.2
        }
        
        scores['overall_confidence'] = sum(scores[key] * weight for key, weight in weights.items())
        scores['confidence_level'] = self._get_confidence_level(scores['overall_confidence'])
        
        return scores
    
    def _get_confidence_level(self, score: float) -> str:
        """Convert confidence score to human-readable level"""
        if score >= 0.8:
            return "High"
        elif score >= 0.6:
            return "Medium"
        elif score >= 0.4:
            return "Low"
        else:
            return "Very Low"
    
    def _query_gemini(self, prompt: str, insight_type: str) -> Dict:
        """Query Gemini API with error handling and retries"""
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Generating {insight_type} insights (attempt {attempt + 1})")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=GEMINI_TEMPERATURE,
                        max_output_tokens=GEMINI_MAX_TOKENS,
                    )
                )
                
                # Extract JSON from response
                response_text = response.text
                
                # Try to parse JSON from the response
                try:
                    # Look for JSON content between ```json and ``` or just parse the whole response
                    if '```json' in response_text:
                        json_start = response_text.find('```json') + 7
                        json_end = response_text.find('```', json_start)
                        json_text = response_text[json_start:json_end].strip()
                    elif '{' in response_text and '}' in response_text:
                        json_start = response_text.find('{')
                        json_end = response_text.rfind('}') + 1
                        json_text = response_text[json_start:json_end]
                    else:
                        json_text = response_text
                    
                    result = json.loads(json_text)
                    logger.info(f"Successfully generated {insight_type} insights")
                    return result
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON for {insight_type}, returning raw text")
                    return {"raw_response": response_text, "parsed": False}
                
            except Exception as e:
                logger.error(f"Error generating {insight_type} insights (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {"error": str(e), "type": insight_type}
        
        return {"error": "Max retries exceeded", "type": insight_type}

def save_insights_to_json(insights: Dict, filepath: str):
    """Save insights to JSON file with proper formatting"""
    logger.info(f"Saving insights to {filepath}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)
    
    logger.info("Insights saved successfully")

if __name__ == "__main__":
    # Example usage - requires API key and data
    print("AI insights module ready!")
