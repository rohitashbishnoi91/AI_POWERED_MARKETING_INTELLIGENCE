"""
Streamlit app launcher for AI-Powered Market Intelligence System
"""

import streamlit as st
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.query_interface import QueryInterface
import pandas as pd

# Set page config first - must be the very first Streamlit command
st.set_page_config(
    page_title="AI-Powered Market Intelligence",
    page_icon="🚀",
    layout="wide"
)

def main():
    """Main Streamlit app"""
    # Check for data files
    processed_dir = "data/processed"
    outputs_dir = "outputs"
    
    if not os.path.exists(processed_dir) or not os.listdir(processed_dir):
        st.error("No processed data found. Please run the pipeline first:")
        st.code("python main.py pipeline --data data/raw/googleplaystore.csv")
        st.info("Or try the demo mode:")
        st.code("python main.py demo")
        return
    
    # Find the most recent data files
    data_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
    insights_files = [f for f in os.listdir(outputs_dir) if f.endswith('.json')] if os.path.exists(outputs_dir) else []
    
    if not data_files:
        st.error("No CSV data files found in data/processed/")
        return
    
    data_path = os.path.join(processed_dir, sorted(data_files)[-1])
    insights_path = os.path.join(outputs_dir, sorted(insights_files)[-1]) if insights_files else ""
    
    # Initialize and run the query interface
    try:
        query_interface = QueryInterface(data_path, insights_path)
        # Don't call run_streamlit_app() as it tries to set page config again
        # Instead, directly call the interface content
        query_interface._run_streamlit_content()
    except Exception as e:
        st.error(f"Error loading application: {e}")
        st.info("Please ensure the data pipeline has been run successfully.")

if __name__ == "__main__":
    main()
