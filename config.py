"""
Configuration settings for the AI-powered market intelligence system
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration - Handle both local .env and Streamlit secrets
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

# Try to get from Streamlit secrets if available and secrets exist
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        try:
            # Only try to access secrets if they exist
            GEMINI_API_KEY = GEMINI_API_KEY or st.secrets.get('GEMINI_API_KEY')
            RAPIDAPI_KEY = RAPIDAPI_KEY or st.secrets.get('RAPIDAPI_KEY')
        except FileNotFoundError:
            # Secrets file not found - this is fine for local development
            pass
        except Exception:
            # Any other secrets-related error - continue without secrets
            pass
except ImportError:
    # Streamlit not available - this is fine
    pass

# Gemini Model Settings
GEMINI_MODEL = 'gemini-2.0-flash-exp'  # Using Gemini 2.5 Flash
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_TOKENS = 8192

# Data paths
DATA_DIR = 'data'
RAW_DATA_DIR = f'{DATA_DIR}/raw'
PROCESSED_DATA_DIR = f'{DATA_DIR}/processed'
REPORTS_DIR = 'reports'
OUTPUTS_DIR = 'outputs'

# RapidAPI Settings
RAPIDAPI_HOST = "app-store-scraper.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"

# Rate limiting
API_RATE_LIMIT_DELAY = 1.0  # seconds between API calls
MAX_RETRIES = 3

# Data validation thresholds
MIN_CONFIDENCE_SCORE = 0.6
MIN_SAMPLE_SIZE = 10

# Report settings
REPORT_TITLE = "AI-Powered Market Intelligence Report"
COMPANY_NAME = "Next-Gen AI Marketing Company"
