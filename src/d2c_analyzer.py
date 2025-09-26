"""
Phase 5 Extension: D2C Funnel Analysis and Creative Content Generation
"""

import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import google.generativeai as genai

from config import *

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class D2CFunnelAnalyzer:
    """Analyze D2C eCommerce funnel metrics and generate insights"""
    
    def __init__(self, data_path: str, ai_generator=None):
        """Initialize the D2C analyzer"""
        self.data_path = data_path
        self.ai_generator = ai_generator
        self.data = None
        self.funnel_metrics = None
        self.seo_metrics = None
        self.creative_outputs = None
        
        self.load_data()
    
    def load_data(self):
        """Load and validate D2C dataset"""
        try:
            logger.info(f"Loading D2C data from {self.data_path}")
            
            # Try reading as Excel first, then CSV
            if self.data_path.endswith('.xlsx') or self.data_path.endswith('.xls'):
                self.data = pd.read_excel(self.data_path)
            else:
                self.data = pd.read_csv(self.data_path)
            
            logger.info(f"Loaded {len(self.data)} rows and {len(self.data.columns)} columns")
            logger.info(f"Columns: {list(self.data.columns)}")
            
            # Validate required columns
            self._validate_data_structure()
            
        except Exception as e:
            logger.error(f"Error loading D2C data: {e}")
            # Create sample data for demonstration
            self.data = self._create_sample_d2c_data()
            logger.info("Created sample D2C data for demonstration")
    
    def _validate_data_structure(self):
        """Validate that the data has required columns for D2C analysis"""
        required_columns = {
            'campaign_metrics': ['campaign_id', 'spend', 'impressions', 'clicks', 'ctr', 'conversions', 'revenue'],
            'funnel_metrics': ['installs', 'signups', 'first_purchase', 'repeat_purchase'],
            'seo_metrics': ['category', 'search_volume', 'avg_position', 'conversion_rate']
        }
        
        missing_columns = []
        for category, columns in required_columns.items():
            for col in columns:
                if col not in self.data.columns:
                    # Try to find similar column names
                    similar_cols = [c for c in self.data.columns if col.lower() in c.lower() or c.lower() in col.lower()]
                    if not similar_cols:
                        missing_columns.append(col)
        
        if missing_columns:
            logger.warning(f"Missing columns for full analysis: {missing_columns}")
        
        return len(missing_columns) == 0
    
    def _create_sample_d2c_data(self) -> pd.DataFrame:
        """Create sample D2C data for demonstration"""
        np.random.seed(42)
        n_rows = 100
        
        categories = ['Electronics', 'Fashion', 'Home & Garden', 'Health & Beauty', 'Sports', 'Books']
        campaign_types = ['Google Ads', 'Facebook Ads', 'Instagram Ads', 'TikTok Ads', 'Pinterest Ads']
        
        sample_data = pd.DataFrame({
            'campaign_id': [f'CAMP_{i:03d}' for i in range(1, n_rows + 1)],
            'category': np.random.choice(categories, n_rows),
            'campaign_type': np.random.choice(campaign_types, n_rows),
            'spend': np.random.uniform(100, 5000, n_rows).round(2),
            'impressions': np.random.randint(1000, 100000, n_rows),
            'clicks': np.random.randint(50, 5000, n_rows),
            'conversions': np.random.randint(5, 200, n_rows),
            'revenue': np.random.uniform(200, 15000, n_rows).round(2),
            'installs': np.random.randint(100, 2000, n_rows),
            'signups': np.random.randint(50, 1500, n_rows),
            'first_purchase': np.random.randint(10, 500, n_rows),
            'repeat_purchase': np.random.randint(2, 150, n_rows),
            'search_volume': np.random.randint(100, 10000, n_rows),
            'avg_position': np.random.uniform(1, 20, n_rows).round(1),
            'conversion_rate': np.random.uniform(0.01, 0.15, n_rows).round(4)
        })
        
        # Calculate derived metrics
        sample_data['ctr'] = (sample_data['clicks'] / sample_data['impressions']).round(4)
        sample_data['cpc'] = (sample_data['spend'] / sample_data['clicks']).round(2)
        sample_data['cpa'] = (sample_data['spend'] / sample_data['conversions']).round(2)
        sample_data['roas'] = (sample_data['revenue'] / sample_data['spend']).round(2)
        
        return sample_data
    
    def analyze_conversion_funnel(self) -> Dict:
        """Analyze the conversion funnel and calculate key metrics"""
        logger.info("Analyzing conversion funnel...")
        
        if self.data is None:
            return {"error": "No data available for analysis"}
        
        funnel_analysis = {}
        
        # Calculate funnel conversion rates
        if all(col in self.data.columns for col in ['installs', 'signups', 'first_purchase', 'repeat_purchase']):
            funnel_stages = {
                'installs_to_signups': self.data['signups'] / self.data['installs'],
                'signups_to_first_purchase': self.data['first_purchase'] / self.data['signups'],
                'first_to_repeat_purchase': self.data['repeat_purchase'] / self.data['first_purchase']
            }
            
            funnel_analysis['conversion_rates'] = {
                stage: {
                    'mean': float(rates.mean()),
                    'median': float(rates.median()),
                    'std': float(rates.std())
                }
                for stage, rates in funnel_stages.items()
            }
        
        # Calculate Customer Acquisition Cost (CAC)
        if 'spend' in self.data.columns and 'conversions' in self.data.columns:
            cac = self.data['spend'] / self.data['conversions']
            funnel_analysis['cac'] = {
                'average': float(cac.mean()),
                'median': float(cac.median()),
                'by_category': self.data.groupby('category')['spend'].sum() / self.data.groupby('category')['conversions'].sum() if 'category' in self.data.columns else {}
            }
        
        # Calculate Return on Ad Spend (ROAS)
        if 'revenue' in self.data.columns and 'spend' in self.data.columns:
            roas = self.data['revenue'] / self.data['spend']
            funnel_analysis['roas'] = {
                'average': float(roas.mean()),
                'median': float(roas.median()),
                'by_category': (self.data.groupby('category')['revenue'].sum() / self.data.groupby('category')['spend'].sum()).to_dict() if 'category' in self.data.columns else {}
            }
        
        # Lifetime Value (LTV) estimation
        if 'repeat_purchase' in self.data.columns and 'revenue' in self.data.columns:
            # Simple LTV estimation based on repeat purchase behavior
            avg_order_value = self.data['revenue'] / self.data['conversions']
            repeat_rate = self.data['repeat_purchase'] / self.data['first_purchase']
            estimated_ltv = avg_order_value * (1 + repeat_rate)
            
            funnel_analysis['ltv'] = {
                'estimated_average': float(estimated_ltv.mean()),
                'avg_order_value': float(avg_order_value.mean()),
                'repeat_purchase_rate': float(repeat_rate.mean())
            }
        
        # Retention patterns
        if 'repeat_purchase' in self.data.columns and 'first_purchase' in self.data.columns:
            retention_analysis = self._analyze_retention_patterns()
            funnel_analysis['retention'] = retention_analysis
        
        self.funnel_metrics = funnel_analysis
        return funnel_analysis
    
    def analyze_seo_opportunities(self) -> Dict:
        """Analyze SEO performance and identify opportunities"""
        logger.info("Analyzing SEO opportunities...")
        
        if self.data is None:
            return {"error": "No data available for analysis"}
        
        seo_analysis = {}
        
        # SEO performance by category
        if all(col in self.data.columns for col in ['category', 'search_volume', 'avg_position', 'conversion_rate']):
            seo_by_category = self.data.groupby('category').agg({
                'search_volume': ['sum', 'mean'],
                'avg_position': 'mean',
                'conversion_rate': 'mean'
            }).round(3)
            
            seo_by_category.columns = ['total_search_volume', 'avg_search_volume', 'avg_position', 'avg_conversion_rate']
            
            # Identify opportunities (high volume, poor position)
            opportunities = seo_by_category[
                (seo_by_category['avg_position'] > 5) & 
                (seo_by_category['total_search_volume'] > seo_by_category['total_search_volume'].median())
            ].sort_values('total_search_volume', ascending=False)
            
            seo_analysis['category_performance'] = seo_by_category.to_dict('index')
            seo_analysis['improvement_opportunities'] = opportunities.head(5).to_dict('index')
        
        # Search volume vs. conversion analysis
        if 'search_volume' in self.data.columns and 'conversion_rate' in self.data.columns:
            # Calculate correlation between search volume and conversion rate
            correlation = self.data['search_volume'].corr(self.data['conversion_rate'])
            seo_analysis['volume_conversion_correlation'] = float(correlation)
            
            # Identify high-potential keywords (high volume, high conversion)
            high_potential = self.data[
                (self.data['search_volume'] > self.data['search_volume'].quantile(0.75)) &
                (self.data['conversion_rate'] > self.data['conversion_rate'].quantile(0.75))
            ]['category'].value_counts().head(5).to_dict()
            
            seo_analysis['high_potential_categories'] = high_potential
        
        # Position improvement opportunities
        if 'avg_position' in self.data.columns:
            position_analysis = {
                'avg_position_overall': float(self.data['avg_position'].mean()),
                'categories_needing_improvement': self.data[self.data['avg_position'] > 10]['category'].value_counts().head(5).to_dict(),
                'top_performing_positions': self.data[self.data['avg_position'] <= 3]['category'].value_counts().head(5).to_dict()
            }
            seo_analysis['position_analysis'] = position_analysis
        
        self.seo_metrics = seo_analysis
        return seo_analysis
    
    def _analyze_retention_patterns(self) -> Dict:
        """Analyze customer retention patterns"""
        retention_analysis = {}
        
        # Calculate repeat purchase rate by category
        if 'category' in self.data.columns:
            category_retention = self.data.groupby('category').apply(
                lambda x: (x['repeat_purchase'].sum() / x['first_purchase'].sum()) if x['first_purchase'].sum() > 0 else 0
            ).to_dict()
            retention_analysis['by_category'] = category_retention
        
        # Overall retention metrics
        total_first_purchases = self.data['first_purchase'].sum()
        total_repeat_purchases = self.data['repeat_purchase'].sum()
        overall_retention = total_repeat_purchases / total_first_purchases if total_first_purchases > 0 else 0
        
        retention_analysis['overall_retention_rate'] = float(overall_retention)
        retention_analysis['total_first_purchases'] = int(total_first_purchases)
        retention_analysis['total_repeat_purchases'] = int(total_repeat_purchases)
        
        return retention_analysis
    
    def generate_creative_content(self) -> Dict:
        """Generate AI-powered creative content based on insights"""
        logger.info("Generating AI-powered creative content...")
        
        if not self.ai_generator:
            logger.warning("No AI generator available. Creating template content.")
            return self._generate_template_creative_content()
        
        if not self.funnel_metrics or not self.seo_metrics:
            # Run analysis first
            self.analyze_conversion_funnel()
            self.analyze_seo_opportunities()
        
        creative_outputs = {}
        
        # Generate ad headlines
        creative_outputs['ad_headlines'] = self._generate_ad_headlines()
        
        # Generate SEO meta descriptions
        creative_outputs['seo_meta_descriptions'] = self._generate_seo_meta_descriptions()
        
        # Generate product description texts
        creative_outputs['product_descriptions'] = self._generate_product_descriptions()
        
        # Generate social media content
        creative_outputs['social_media_content'] = self._generate_social_content()
        
        self.creative_outputs = creative_outputs
        return creative_outputs
    
    def _generate_ad_headlines(self) -> List[Dict]:
        """Generate AI-powered ad headlines"""
        if not self.ai_generator:
            return self._get_template_ad_headlines()
        
        # Get top performing categories for context
        top_categories = list(self.data['category'].value_counts().head(3).index) if 'category' in self.data.columns else ['Electronics', 'Fashion', 'Home']
        
        # Get performance metrics for context
        avg_roas = self.funnel_metrics.get('roas', {}).get('average', 2.5)
        avg_conversion_rate = self.data['conversion_rate'].mean() if 'conversion_rate' in self.data.columns else 0.05
        
        prompt = f"""
        Based on D2C eCommerce performance data, generate compelling ad headlines:
        
        Context:
        - Top performing categories: {top_categories}
        - Average ROAS: {avg_roas:.2f}
        - Average conversion rate: {avg_conversion_rate:.2%}
        - Target audience: Online shoppers interested in quality products
        
        Generate 5 ad headlines for each category that are:
        - Compelling and action-oriented
        - Highlight value propositions
        - Include urgency or scarcity elements
        - Maximum 30 characters each
        
        Return in JSON format:
        {{
            "category_name": [
                {{"headline": "text", "focus": "value_prop/urgency/quality", "target_audience": "description"}},
                ...
            ]
        }}
        
        Focus on conversion-optimized copy that drives action.
        """
        
        result = self.ai_generator._query_gemini(prompt, "ad_headlines")
        
        if isinstance(result, dict) and not result.get('error'):
            return result
        else:
            logger.warning("AI generation failed, using template headlines")
            return self._get_template_ad_headlines()
    
    def _generate_seo_meta_descriptions(self) -> List[Dict]:
        """Generate SEO meta descriptions"""
        if not self.ai_generator:
            return self._get_template_meta_descriptions()
        
        # Get SEO opportunities
        seo_opportunities = self.seo_metrics.get('improvement_opportunities', {})
        high_potential = self.seo_metrics.get('high_potential_categories', {})
        
        prompt = f"""
        Generate SEO meta descriptions for D2C eCommerce categories:
        
        SEO Context:
        - Categories needing improvement: {list(seo_opportunities.keys())[:3]}
        - High potential categories: {list(high_potential.keys())[:3]}
        - Average search position: {self.seo_metrics.get('position_analysis', {}).get('avg_position_overall', 8):.1f}
        
        Generate meta descriptions that are:
        - 150-160 characters maximum
        - Include primary keywords naturally
        - Have compelling calls-to-action
        - Highlight unique value propositions
        - Optimized for click-through rates
        
        Return in JSON format:
        {{
            "category_name": [
                {{"meta_description": "text", "target_keywords": ["keyword1", "keyword2"], "cta_type": "shop/discover/explore"}},
                ...
            ]
        }}
        
        Focus on increasing organic click-through rates and search visibility.
        """
        
        result = self.ai_generator._query_gemini(prompt, "seo_meta_descriptions")
        
        if isinstance(result, dict) and not result.get('error'):
            return result
        else:
            logger.warning("AI generation failed, using template meta descriptions")
            return self._get_template_meta_descriptions()
    
    def _generate_product_descriptions(self) -> List[Dict]:
        """Generate product description texts"""
        if not self.ai_generator:
            return self._get_template_product_descriptions()
        
        # Get conversion and retention insights
        avg_retention = self.funnel_metrics.get('retention', {}).get('overall_retention_rate', 0.3)
        top_converting_categories = self.funnel_metrics.get('roas', {}).get('by_category', {})
        
        prompt = f"""
        Generate compelling product description templates for D2C eCommerce:
        
        Performance Context:
        - Customer retention rate: {avg_retention:.1%}
        - Top converting categories: {list(top_converting_categories.keys())[:3] if top_converting_categories else ['Electronics', 'Fashion', 'Home']}
        - Focus on conversion optimization and customer satisfaction
        
        Generate product description templates that:
        - Highlight key benefits and features
        - Address customer pain points
        - Include social proof elements
        - Have clear value propositions
        - Drive purchase decisions
        - Are 100-200 words each
        
        Return in JSON format:
        {{
            "category_name": [
                {{
                    "description_template": "text with [PRODUCT_NAME] placeholders",
                    "key_benefits": ["benefit1", "benefit2", "benefit3"],
                    "target_pain_points": ["pain1", "pain2"],
                    "social_proof_angle": "description"
                }},
                ...
            ]
        }}
        
        Focus on conversion-optimized copy that builds trust and drives sales.
        """
        
        result = self.ai_generator._query_gemini(prompt, "product_descriptions")
        
        if isinstance(result, dict) and not result.get('error'):
            return result
        else:
            logger.warning("AI generation failed, using template product descriptions")
            return self._get_template_product_descriptions()
    
    def _generate_social_content(self) -> List[Dict]:
        """Generate social media content"""
        if not self.ai_generator:
            return self._get_template_social_content()
        
        # Use performance data for context
        best_categories = list(self.data['category'].value_counts().head(3).index) if 'category' in self.data.columns else ['Electronics', 'Fashion', 'Home']
        
        prompt = f"""
        Generate social media content for D2C eCommerce brand:
        
        Brand Context:
        - Top product categories: {best_categories}
        - Focus on engagement and conversion
        - Target audience: Quality-conscious online shoppers
        
        Generate social media posts for different platforms:
        - Instagram: Visual-focused, lifestyle-oriented
        - Facebook: Community-building, value-focused
        - TikTok: Trend-aware, entertaining
        - Twitter: News-worthy, conversation-starting
        
        Return in JSON format:
        {{
            "platform": [
                {{
                    "post_text": "text content",
                    "hashtags": ["#hashtag1", "#hashtag2"],
                    "content_type": "product_showcase/lifestyle/educational/ugc",
                    "engagement_goal": "likes/shares/comments/clicks"
                }},
                ...
            ]
        }}
        
        Focus on authentic, engaging content that drives brand awareness and sales.
        """
        
        result = self.ai_generator._query_gemini(prompt, "social_content")
        
        if isinstance(result, dict) and not result.get('error'):
            return result
        else:
            logger.warning("AI generation failed, using template social content")
            return self._get_template_social_content()
    
    def _generate_template_creative_content(self) -> Dict:
        """Generate template creative content when AI is not available"""
        return {
            'ad_headlines': self._get_template_ad_headlines(),
            'seo_meta_descriptions': self._get_template_meta_descriptions(),
            'product_descriptions': self._get_template_product_descriptions(),
            'social_media_content': self._get_template_social_content()
        }
    
    def _get_template_ad_headlines(self) -> Dict:
        """Template ad headlines"""
        return {
            "Electronics": [
                {"headline": "Tech That Works For You", "focus": "quality", "target_audience": "tech enthusiasts"},
                {"headline": "Upgrade Your Setup Today", "focus": "urgency", "target_audience": "professionals"},
                {"headline": "Premium Electronics, Fair Prices", "focus": "value_prop", "target_audience": "budget-conscious"}
            ],
            "Fashion": [
                {"headline": "Style That Speaks Volumes", "focus": "quality", "target_audience": "fashion-forward"},
                {"headline": "Limited Collection Available", "focus": "urgency", "target_audience": "trendsetters"},
                {"headline": "Designer Look, Everyday Price", "focus": "value_prop", "target_audience": "value seekers"}
            ]
        }
    
    def _get_template_meta_descriptions(self) -> Dict:
        """Template meta descriptions"""
        return {
            "Electronics": [
                {
                    "meta_description": "Discover cutting-edge electronics at unbeatable prices. Free shipping, warranty included. Shop now for the latest tech innovations.",
                    "target_keywords": ["electronics", "tech", "gadgets"],
                    "cta_type": "shop"
                }
            ],
            "Fashion": [
                {
                    "meta_description": "Elevate your style with our curated fashion collection. Trendy, affordable, sustainable. Free returns. Explore our latest arrivals today.",
                    "target_keywords": ["fashion", "clothing", "style"],
                    "cta_type": "explore"
                }
            ]
        }
    
    def _get_template_product_descriptions(self) -> Dict:
        """Template product descriptions"""
        return {
            "Electronics": [
                {
                    "description_template": "Experience the future with [PRODUCT_NAME]. Engineered for performance, designed for life. Features cutting-edge technology that adapts to your needs. Trusted by thousands of customers worldwide.",
                    "key_benefits": ["Performance", "Reliability", "Innovation"],
                    "target_pain_points": ["Outdated technology", "Poor reliability"],
                    "social_proof_angle": "Trusted by thousands worldwide"
                }
            ]
        }
    
    def _get_template_social_content(self) -> Dict:
        """Template social content"""
        return {
            "Instagram": [
                {
                    "post_text": "✨ Transform your space with our latest collection. Swipe to see the magic! ➡️",
                    "hashtags": ["#homedecor", "#lifestyle", "#design"],
                    "content_type": "product_showcase",
                    "engagement_goal": "likes"
                }
            ],
            "Facebook": [
                {
                    "post_text": "Did you know? Our customers save an average of 30% compared to traditional retail. Join our community of smart shoppers!",
                    "hashtags": ["#savings", "#community", "#smartshopping"],
                    "content_type": "educational",
                    "engagement_goal": "shares"
                }
            ]
        }
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive D2C analysis report"""
        logger.info("Generating comprehensive D2C analysis report...")
        
        # Run all analyses
        funnel_analysis = self.analyze_conversion_funnel()
        seo_analysis = self.analyze_seo_opportunities()
        creative_content = self.generate_creative_content()
        
        # Compile comprehensive report
        report = {
            'executive_summary': self._generate_d2c_executive_summary(),
            'funnel_analysis': funnel_analysis,
            'seo_analysis': seo_analysis,
            'creative_content': creative_content,
            'key_recommendations': self._generate_d2c_recommendations(),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_size': len(self.data),
                'analysis_type': 'D2C_Funnel_And_SEO'
            }
        }
        
        return report
    
    def _generate_d2c_executive_summary(self) -> List[str]:
        """Generate executive summary for D2C analysis"""
        summary_points = []
        
        if self.funnel_metrics:
            # ROAS summary
            avg_roas = self.funnel_metrics.get('roas', {}).get('average', 0)
            if avg_roas > 3:
                summary_points.append(f"Strong ROAS performance at {avg_roas:.2f}x, indicating efficient ad spend")
            elif avg_roas > 2:
                summary_points.append(f"Moderate ROAS at {avg_roas:.2f}x with room for optimization")
            else:
                summary_points.append(f"ROAS at {avg_roas:.2f}x requires immediate attention and optimization")
            
            # CAC summary
            avg_cac = self.funnel_metrics.get('cac', {}).get('average', 0)
            if avg_cac > 0:
                summary_points.append(f"Customer acquisition cost averaging ${avg_cac:.2f}")
            
            # Retention summary
            retention_rate = self.funnel_metrics.get('retention', {}).get('overall_retention_rate', 0)
            if retention_rate > 0.4:
                summary_points.append(f"Strong customer retention at {retention_rate:.1%}")
            elif retention_rate > 0.2:
                summary_points.append(f"Moderate retention rate of {retention_rate:.1%} with improvement potential")
            else:
                summary_points.append(f"Low retention rate of {retention_rate:.1%} needs strategic focus")
        
        if self.seo_metrics:
            # SEO opportunities summary
            opportunities = len(self.seo_metrics.get('improvement_opportunities', {}))
            if opportunities > 0:
                summary_points.append(f"Identified {opportunities} high-impact SEO improvement opportunities")
        
        if not summary_points:
            summary_points = ["D2C analysis completed with performance insights and optimization recommendations"]
        
        return summary_points
    
    def _generate_d2c_recommendations(self) -> Dict:
        """Generate strategic recommendations for D2C business"""
        recommendations = {
            'funnel_optimization': [],
            'seo_improvements': [],
            'creative_strategy': [],
            'investment_priorities': []
        }
        
        if self.funnel_metrics:
            # Funnel optimization recommendations
            avg_roas = self.funnel_metrics.get('roas', {}).get('average', 0)
            if avg_roas < 2:
                recommendations['funnel_optimization'].append("Immediate focus on improving ROAS through better targeting and creative optimization")
            
            retention_rate = self.funnel_metrics.get('retention', {}).get('overall_retention_rate', 0)
            if retention_rate < 0.3:
                recommendations['funnel_optimization'].append("Implement customer retention program to increase repeat purchase rates")
            
            # Investment priorities based on performance
            if avg_roas > 3:
                recommendations['investment_priorities'].append("Scale high-performing campaigns for maximum ROI")
            else:
                recommendations['investment_priorities'].append("Focus on conversion rate optimization before scaling spend")
        
        if self.seo_metrics:
            # SEO improvement recommendations
            opportunities = self.seo_metrics.get('improvement_opportunities', {})
            if opportunities:
                top_opportunity = list(opportunities.keys())[0] if opportunities else None
                if top_opportunity:
                    recommendations['seo_improvements'].append(f"Prioritize SEO optimization for {top_opportunity} category")
            
            avg_position = self.seo_metrics.get('position_analysis', {}).get('avg_position_overall', 10)
            if avg_position > 5:
                recommendations['seo_improvements'].append("Focus on improving search rankings through content optimization and link building")
        
        # Creative strategy recommendations
        if self.creative_outputs:
            recommendations['creative_strategy'].append("Implement A/B testing for generated ad headlines and product descriptions")
            recommendations['creative_strategy'].append("Deploy SEO-optimized meta descriptions for improved organic click-through rates")
        
        return recommendations

def save_d2c_analysis(analysis_results: Dict, output_path: str):
    """Save D2C analysis results to JSON"""
    logger.info(f"Saving D2C analysis to {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    logger.info("D2C analysis saved successfully")

if __name__ == "__main__":
    # Example usage
    print("D2C Funnel Analyzer module ready!")
    
    # Demo usage
    # analyzer = D2CFunnelAnalyzer('data/d2c_sample.xlsx')
    # funnel_insights = analyzer.analyze_conversion_funnel()
    # seo_insights = analyzer.analyze_seo_opportunities()
    # creative_content = analyzer.generate_creative_content()
    # full_report = analyzer.generate_comprehensive_report()
