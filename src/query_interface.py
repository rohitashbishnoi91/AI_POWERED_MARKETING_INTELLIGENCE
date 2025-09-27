"""
Query interface for interacting with market intelligence insights
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import logging

from config import *

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryInterface:
    """Interactive query interface for market intelligence data"""
    
    def __init__(self, data_path: str, insights_path: str):
        """Initialize the query interface"""
        self.data_path = data_path
        self.insights_path = insights_path
        self.data = None
        self.insights = None
        self.load_data()
    
    def load_data(self):
        """Load processed data and insights"""
        try:
            self.data = pd.read_csv(self.data_path)
            logger.info(f"Loaded {len(self.data)} records from {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.data = pd.DataFrame()
        
        try:
            with open(self.insights_path, 'r', encoding='utf-8') as f:
                self.insights = json.load(f)
            logger.info(f"Loaded insights from {self.insights_path}")
        except Exception as e:
            logger.error(f"Error loading insights: {e}")
            self.insights = {}
    
    def run_streamlit_app(self):
        """Run the Streamlit web interface"""
        st.set_page_config(
            page_title="AI-Powered Market Intelligence",
            page_icon="📊",
            layout="wide"
        )
        
        self._run_streamlit_content()
    
    def _run_streamlit_content(self):
        """Run the Streamlit content without page config"""
        st.title("🚀 AI-Powered Market Intelligence Dashboard")
        st.markdown("---")
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a section:",
            ["Overview", "Data Explorer", "AI Insights", "Category Analysis", "Competitive Intelligence", "Query Assistant"]
        )
        
        if page == "Overview":
            self._show_overview()
        elif page == "Data Explorer":
            self._show_data_explorer()
        elif page == "AI Insights":
            self._show_ai_insights()
        elif page == "Category Analysis":
            self._show_category_analysis()
        elif page == "Competitive Intelligence":
            self._show_competitive_intelligence()
        elif page == "Query Assistant":
            self._show_query_assistant()
    
    def _show_overview(self):
        """Display system overview and key metrics"""
        st.header("📈 Market Intelligence Overview")
        
        if self.data.empty:
            st.error("No data available. Please ensure data is loaded correctly.")
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Apps", len(self.data))
        
        with col2:
            avg_rating = self.data['rating'].mean() if 'rating' in self.data.columns else 0
            st.metric("Avg Rating", f"{avg_rating:.2f}")
        
        with col3:
            free_percentage = (self.data['is_free'].mean() * 100) if 'is_free' in self.data.columns else 0
            st.metric("Free Apps", f"{free_percentage:.1f}%")
        
        with col4:
            categories = self.data['category'].nunique() if 'category' in self.data.columns else 0
            st.metric("Categories", categories)
        
        # Data sources breakdown
        st.subheader("Data Sources")
        if 'data_source' in self.data.columns:
            source_counts = self.data['data_source'].value_counts()
            fig = px.pie(values=source_counts.values, names=source_counts.index, title="Data Sources Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Confidence scores
        if self.insights and 'confidence_scores' in self.insights:
            st.subheader("Data Quality & Confidence")
            conf_scores = self.insights['confidence_scores']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Confidence", f"{conf_scores.get('overall_confidence', 0):.2f}")
                st.metric("Confidence Level", conf_scores.get('confidence_level', 'Unknown'))
            
            with col2:
                st.metric("Data Completeness", f"{conf_scores.get('overall_completeness', 0):.2f}")
                st.metric("Sample Size Confidence", f"{conf_scores.get('sample_size_confidence', 0):.2f}")
    
    def _show_data_explorer(self):
        """Interactive data exploration interface"""
        st.header("🔍 Data Explorer")
        
        if self.data.empty:
            st.error("No data available.")
            return
        
        # Filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'category' in self.data.columns:
                categories = ['All'] + list(self.data['category'].unique())
                selected_category = st.selectbox("Category", categories)
            else:
                selected_category = 'All'
        
        with col2:
            if 'data_source' in self.data.columns:
                sources = ['All'] + list(self.data['data_source'].unique())
                selected_source = st.selectbox("Data Source", sources)
            else:
                selected_source = 'All'
        
        with col3:
            if 'rating' in self.data.columns:
                min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
            else:
                min_rating = 0.0
        
        # Apply filters
        filtered_data = self.data.copy()
        if selected_category != 'All' and 'category' in self.data.columns:
            filtered_data = filtered_data[filtered_data['category'] == selected_category]
        if selected_source != 'All' and 'data_source' in self.data.columns:
            filtered_data = filtered_data[filtered_data['data_source'] == selected_source]
        if 'rating' in self.data.columns:
            filtered_data = filtered_data[filtered_data['rating'] >= min_rating]
        
        st.write(f"Showing {len(filtered_data)} apps")
        
        # Charts with error handling
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                if 'category' in filtered_data.columns and len(filtered_data) > 0:
                    cat_counts = filtered_data['category'].value_counts().head(10)
                    if len(cat_counts) > 0:
                        fig = px.bar(x=cat_counts.values, y=cat_counts.index, orientation='h', 
                                   title="Top 10 Categories")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No category data available for current filters")
                else:
                    st.info("Category data not available")
            except Exception as e:
                st.error(f"Error creating category chart: {str(e)}")
                logger.error(f"Category chart error: {e}")
        
        with col2:
            try:
                if 'rating' in filtered_data.columns and len(filtered_data) > 0:
                    ratings = filtered_data['rating'].dropna()
                    if len(ratings) > 0:
                        fig = px.histogram(ratings, title="Rating Distribution", nbins=20)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No rating data available for current filters")
                else:
                    st.info("Rating data not available")
            except Exception as e:
                st.error(f"Error creating rating chart: {str(e)}")
                logger.error(f"Rating chart error: {e}")
        
        # Data table with error handling
        st.subheader("Data Table")
        try:
            display_columns = [col for col in ['app_name', 'category', 'rating', 'review_count', 'price_usd', 'is_free'] 
                              if col in filtered_data.columns]
            if display_columns and len(filtered_data) > 0:
                st.dataframe(filtered_data[display_columns].head(100), use_container_width=True)
            else:
                st.info("No data available to display")
        except Exception as e:
            st.error(f"Error displaying data table: {str(e)}")
            logger.error(f"Data table error: {e}")
    
    def _show_ai_insights(self):
        """Display AI-generated insights"""
        st.header("🤖 AI-Generated Insights")
        
        if not self.insights:
            st.error("No insights available. Please generate insights first.")
            return
        
        # Market Overview
        if 'market_overview' in self.insights:
            st.subheader("📊 Market Overview")
            overview = self.insights['market_overview']
            
            if 'key_findings' in overview:
                st.write("**Key Findings:**")
                for finding in overview['key_findings']:
                    st.write(f"• {finding}")
            
            if 'market_size_assessment' in overview:
                st.write("**Market Size Assessment:**")
                st.write(overview['market_size_assessment'])
        
        # User Behavior Insights
        if 'user_behavior_insights' in self.insights:
            st.subheader("👥 User Behavior Insights")
            behavior = self.insights['user_behavior_insights']
            
            col1, col2 = st.columns(2)
            with col1:
                if 'user_preferences' in behavior:
                    st.write("**User Preferences:**")
                    for pref in behavior['user_preferences']:
                        st.write(f"• {pref}")
            
            with col2:
                if 'engagement_patterns' in behavior:
                    st.write("**Engagement Patterns:**")
                    for pattern in behavior['engagement_patterns']:
                        st.write(f"• {pattern}")
        
        # Opportunities & Threats
        if 'opportunities_threats' in self.insights:
            st.subheader("🎯 Opportunities & Threats")
            ot = self.insights['opportunities_threats']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Opportunities:**")
                if 'market_opportunities' in ot:
                    for opp in ot['market_opportunities']:
                        if isinstance(opp, dict):
                            st.write(f"• {opp.get('opportunity', opp)} ({opp.get('potential_impact', 'Unknown')} impact)")
                        else:
                            st.write(f"• {opp}")
            
            with col2:
                st.write("**Threats:**")
                if 'market_threats' in ot:
                    for threat in ot['market_threats']:
                        if isinstance(threat, dict):
                            st.write(f"• {threat.get('threat', threat)} ({threat.get('risk_level', 'Unknown')} risk)")
                        else:
                            st.write(f"• {threat}")
    
    def _show_category_analysis(self):
        """Display category-specific analysis"""
        st.header("📂 Category Analysis")
        
        if self.data.empty or 'category' not in self.data.columns:
            st.error("Category data not available.")
            return
        
        # Category performance metrics
        category_metrics = self.data.groupby('category').agg({
            'rating': 'mean',
            'review_count': 'mean',
            'app_name': 'count'
        }).round(2)
        category_metrics.columns = ['Avg Rating', 'Avg Reviews', 'App Count']
        category_metrics = category_metrics.sort_values('App Count', ascending=False)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(category_metrics.head(15), 
                           x='Avg Rating', y='Avg Reviews', 
                           size='App Count',
                           hover_name=category_metrics.index,
                           title="Category Performance Map")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_cats = category_metrics.head(10)
            fig = px.bar(x=top_cats.index, y=top_cats['App Count'], 
                        title="Top 10 Categories by App Count")
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Category insights from AI
        if self.insights and 'category_analysis' in self.insights:
            st.subheader("🤖 AI Category Insights")
            cat_insights = self.insights['category_analysis']
            
            col1, col2 = st.columns(2)
            with col1:
                if 'most_competitive_categories' in cat_insights:
                    st.write("**Most Competitive:**")
                    for cat in cat_insights['most_competitive_categories']:
                        st.write(f"• {cat}")
            
            with col2:
                if 'underserved_categories' in cat_insights:
                    st.write("**Underserved Categories:**")
                    for cat in cat_insights['underserved_categories']:
                        st.write(f"• {cat}")
        
        # Category details table
        st.subheader("Category Performance Table")
        st.dataframe(category_metrics, use_container_width=True)
    
    def _show_competitive_intelligence(self):
        """Display competitive intelligence"""
        st.header("🥊 Competitive Intelligence")
        
        if self.data.empty:
            st.error("No data available.")
            return
        
        # Top performers
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Rated Apps")
            if 'rating' in self.data.columns:
                top_rated = self.data.nlargest(10, 'rating')[['app_name', 'category', 'rating', 'review_count']]
                st.dataframe(top_rated, use_container_width=True)
        
        with col2:
            st.subheader("📈 Most Reviewed Apps")
            if 'review_count' in self.data.columns:
                most_reviewed = self.data.nlargest(10, 'review_count')[['app_name', 'category', 'rating', 'review_count']]
                st.dataframe(most_reviewed, use_container_width=True)
        
        # Competitive insights from AI
        if self.insights and 'competitive_landscape' in self.insights:
            st.subheader("🤖 AI Competitive Insights")
            comp_insights = self.insights['competitive_landscape']
            
            if 'success_factors' in comp_insights:
                st.write("**Key Success Factors:**")
                for factor in comp_insights['success_factors']:
                    st.write(f"• {factor}")
            
            if 'competitive_gaps' in comp_insights:
                st.write("**Market Gaps:**")
                for gap in comp_insights['competitive_gaps']:
                    st.write(f"• {gap}")
    
    def _show_query_assistant(self):
        """Natural language query assistant"""
        st.header("💬 Query Assistant")
        
        st.info("Ask questions about the market data and get AI-powered answers!")
        
        # Pre-defined queries
        st.subheader("Quick Queries")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("What are the top performing categories?"):
                self._answer_predefined_query("top_categories")
            
            if st.button("Which apps have the best user ratings?"):
                self._answer_predefined_query("best_rated")
        
        with col2:
            if st.button("What are the market opportunities?"):
                self._answer_predefined_query("opportunities")
            
            if st.button("How competitive is the market?"):
                self._answer_predefined_query("competition")
        
        # Custom query input
        st.subheader("Custom Query")
        user_query = st.text_input("Enter your question about the market data:")
        
        if st.button("Ask") and user_query:
            self._answer_custom_query(user_query)
    
    def _answer_predefined_query(self, query_type: str):
        """Answer predefined queries"""
        if query_type == "top_categories" and 'category' in self.data.columns:
            top_cats = self.data['category'].value_counts().head(5)
            st.write("**Top 5 Categories by App Count:**")
            for cat, count in top_cats.items():
                st.write(f"• {cat}: {count} apps")
        
        elif query_type == "best_rated" and 'rating' in self.data.columns:
            top_rated = self.data.nlargest(5, 'rating')[['app_name', 'rating']]
            st.write("**Top 5 Highest Rated Apps:**")
            for _, app in top_rated.iterrows():
                st.write(f"• {app['app_name']}: {app['rating']:.2f} ⭐")
        
        elif query_type == "opportunities":
            if self.insights and 'opportunities_threats' in self.insights:
                opps = self.insights['opportunities_threats'].get('market_opportunities', [])
                st.write("**Market Opportunities:**")
                for opp in opps[:3]:
                    if isinstance(opp, dict):
                        st.write(f"• {opp.get('opportunity', opp)}")
                    else:
                        st.write(f"• {opp}")
        
        elif query_type == "competition":
            if self.insights and 'competitive_landscape' in self.insights:
                comp = self.insights['competitive_landscape']
                if 'success_factors' in comp:
                    st.write("**Key Success Factors in the Market:**")
                    for factor in comp['success_factors'][:3]:
                        st.write(f"• {factor}")
    
    def _answer_custom_query(self, query: str):
        """Answer custom user queries"""
        st.write(f"**Your question:** {query}")
        
        # Simple keyword-based matching for demonstration
        query_lower = query.lower()
        
        if 'category' in query_lower or 'categories' in query_lower:
            if 'category' in self.data.columns:
                cats = self.data['category'].value_counts().head(3)
                st.write("**Top Categories:**")
                for cat, count in cats.items():
                    st.write(f"• {cat}: {count} apps")
        
        elif 'rating' in query_lower or 'rated' in query_lower:
            if 'rating' in self.data.columns:
                avg_rating = self.data['rating'].mean()
                st.write(f"**Average app rating:** {avg_rating:.2f} ⭐")
                
        elif 'price' in query_lower or 'cost' in query_lower or 'free' in query_lower:
            if 'is_free' in self.data.columns:
                free_pct = self.data['is_free'].mean() * 100
                st.write(f"**{free_pct:.1f}%** of apps are free")
        
        else:
            st.write("I can help you with questions about categories, ratings, pricing, and general market trends. Try asking about specific aspects of the data!")

class CLIInterface:
    """Command line interface for querying market intelligence"""
    
    def __init__(self, data_path: str, insights_path: str):
        self.query_interface = QueryInterface(data_path, insights_path)
    
    def run(self):
        """Run the CLI interface"""
        print("\n🚀 AI-Powered Market Intelligence CLI")
        print("=" * 50)
        
        while True:
            print("\nAvailable commands:")
            print("1. overview - Show market overview")
            print("2. categories - Show category analysis")
            print("3. insights - Show AI insights")
            print("4. top_apps - Show top performing apps")
            print("5. query <question> - Ask a custom question")
            print("6. exit - Exit the CLI")
            
            command = input("\nEnter command: ").strip().lower()
            
            if command == "exit":
                break
            elif command == "overview":
                self._show_cli_overview()
            elif command == "categories":
                self._show_cli_categories()
            elif command == "insights":
                self._show_cli_insights()
            elif command == "top_apps":
                self._show_cli_top_apps()
            elif command.startswith("query "):
                question = command[6:]
                self._handle_cli_query(question)
            else:
                print("Unknown command. Please try again.")
    
    def _show_cli_overview(self):
        """Show overview in CLI"""
        data = self.query_interface.data
        print(f"\n📊 Market Overview:")
        print(f"Total Apps: {len(data)}")
        if 'rating' in data.columns:
            print(f"Average Rating: {data['rating'].mean():.2f}")
        if 'category' in data.columns:
            print(f"Categories: {data['category'].nunique()}")
        if 'data_source' in data.columns:
            print(f"Data Sources: {list(data['data_source'].unique())}")
    
    def _show_cli_categories(self):
        """Show category analysis in CLI"""
        data = self.query_interface.data
        if 'category' in data.columns:
            print(f"\n📂 Top 10 Categories:")
            top_cats = data['category'].value_counts().head(10)
            for i, (cat, count) in enumerate(top_cats.items(), 1):
                print(f"{i:2d}. {cat}: {count} apps")
        else:
            print("Category data not available.")
    
    def _show_cli_insights(self):
        """Show AI insights in CLI"""
        insights = self.query_interface.insights
        if insights and 'market_overview' in insights:
            overview = insights['market_overview']
            print(f"\n🤖 AI Insights:")
            if 'key_findings' in overview:
                print("Key Findings:")
                for finding in overview['key_findings']:
                    print(f"• {finding}")
        else:
            print("No AI insights available.")
    
    def _show_cli_top_apps(self):
        """Show top apps in CLI"""
        data = self.query_interface.data
        if 'rating' in data.columns:
            print(f"\n🏆 Top 10 Rated Apps:")
            top_apps = data.nlargest(10, 'rating')[['app_name', 'rating']]
            for i, (_, app) in enumerate(top_apps.iterrows(), 1):
                print(f"{i:2d}. {app['app_name']}: {app['rating']:.2f} ⭐")
        else:
            print("Rating data not available.")
    
    def _handle_cli_query(self, question: str):
        """Handle custom CLI queries"""
        print(f"\n💬 Question: {question}")
        print("Processing...")
        # Simple demonstration - in a real system, this would use NLP/AI
        print("This would process your question using AI. For now, try the predefined commands!")

if __name__ == "__main__":
    # Example usage
    print("Query interface module ready!")
