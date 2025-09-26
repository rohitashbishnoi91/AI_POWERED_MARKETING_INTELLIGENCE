"""
Data pipeline for ingesting, cleaning, and processing market intelligence data
"""

import pandas as pd
import numpy as np
import requests
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

from config import *

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPipeline:
    """Main data pipeline class for handling multiple data sources"""
    
    def __init__(self):
        self.kaggle_data = None
        self.appstore_data = None
        self.combined_data = None
        
    def load_kaggle_data(self, file_path: str) -> pd.DataFrame:
        """Load and perform initial cleaning of Kaggle Google Play Store data"""
        logger.info(f"Loading Kaggle data from {file_path}")
        
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"Successfully loaded data with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not read file with any supported encoding")
                
            logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
            logger.info(f"Columns: {list(df.columns)}")
            
            self.kaggle_data = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading Kaggle data: {e}")
            raise
    
    def clean_kaggle_data(self) -> pd.DataFrame:
        """Clean and normalize the Kaggle Google Play Store data"""
        if self.kaggle_data is None:
            raise ValueError("No Kaggle data loaded. Call load_kaggle_data first.")
        
        logger.info("Starting Kaggle data cleaning...")
        df = self.kaggle_data.copy()
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Clean column names (normalize spacing and case)
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
        
        # Handle common column name variations
        column_mapping = {
            'app': 'app_name',
            'category': 'category',
            'rating': 'rating',
            'reviews': 'review_count',
            'size': 'size',
            'installs': 'installs',
            'type': 'app_type',
            'price': 'price',
            'content_rating': 'content_rating',
            'genres': 'genres',
            'last_updated': 'last_updated',
            'current_ver': 'current_version',
            'android_ver': 'android_version'
        }
        
        # Rename columns if they exist
        existing_columns = {old: new for old, new in column_mapping.items() if old in df.columns}
        df = df.rename(columns=existing_columns)
        
        # Clean rating column
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df['rating'] = df['rating'].clip(0, 5)  # Ratings should be 0-5
        
        # Clean review count
        if 'review_count' in df.columns:
            df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce')
            df['review_count'] = df['review_count'].fillna(0).astype(int)
        
        # Clean installs column
        if 'installs' in df.columns:
            df['installs_clean'] = df['installs'].astype(str).str.replace(',', '').str.replace('+', '')
            df['installs_clean'] = pd.to_numeric(df['installs_clean'], errors='coerce')
            df['installs_clean'] = df['installs_clean'].fillna(0).astype(int)
        
        # Clean size column
        if 'size' in df.columns:
            df['size_mb'] = self._convert_size_to_mb(df['size'])
        
        # Clean price column
        if 'price' in df.columns:
            df['price_usd'] = self._convert_price_to_usd(df['price'])
        
        # Create binary app type column
        if 'app_type' in df.columns:
            df['is_free'] = df['app_type'].str.lower() == 'free'
        
        # Clean category
        if 'category' in df.columns:
            df['category'] = df['category'].str.strip().str.upper()
        
        # Add derived features
        df['data_source'] = 'google_play'
        df['processed_date'] = datetime.now().isoformat()
        
        # Log cleaning results
        logger.info(f"Cleaned data shape: {df.shape}")
        logger.info(f"Missing values per column:\n{df.isnull().sum()}")
        
        self.kaggle_data = df
        return df
    
    def _convert_size_to_mb(self, size_series: pd.Series) -> pd.Series:
        """Convert size strings to MB"""
        def parse_size(size_str):
            if pd.isna(size_str) or size_str == 'Varies with device':
                return np.nan
            
            size_str = str(size_str).upper()
            
            # Extract number and unit
            match = re.search(r'([\d.]+)\s*([KMG]?B?)', size_str)
            if not match:
                return np.nan
            
            number = float(match.group(1))
            unit = match.group(2)
            
            if 'K' in unit:
                return number / 1024  # KB to MB
            elif 'M' in unit:
                return number
            elif 'G' in unit:
                return number * 1024  # GB to MB
            else:
                return number / (1024 * 1024)  # Bytes to MB
        
        return size_series.apply(parse_size)
    
    def _convert_price_to_usd(self, price_series: pd.Series) -> pd.Series:
        """Convert price strings to USD float"""
        def parse_price(price_str):
            if pd.isna(price_str) or price_str == '0' or price_str.lower() == 'free':
                return 0.0
            
            # Remove currency symbols and extract number
            price_str = str(price_str).replace('$', '').replace(',', '')
            
            try:
                return float(price_str)
            except:
                return np.nan
        
        return price_series.apply(parse_price)

class AppStoreAPI:
    """Handle RapidAPI App Store Scraper integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = RAPIDAPI_BASE_URL
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }
        
    def get_app_details(self, app_ids: List[str], max_apps: int = 50) -> List[Dict]:
        """Fetch app details from App Store API"""
        logger.info(f"Fetching details for {min(len(app_ids), max_apps)} apps from App Store API")
        
        apps_data = []
        
        for i, app_id in enumerate(app_ids[:max_apps]):
            if i > 0:
                time.sleep(API_RATE_LIMIT_DELAY)  # Rate limiting
            
            try:
                url = f"{self.base_url}/app-details"
                querystring = {"id": app_id}
                
                response = requests.get(url, headers=self.headers, params=querystring)
                
                if response.status_code == 200:
                    app_data = response.json()
                    apps_data.append(self._normalize_appstore_data(app_data))
                    logger.info(f"Successfully fetched data for app {i+1}/{min(len(app_ids), max_apps)}")
                else:
                    logger.warning(f"Failed to fetch app {app_id}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error fetching app {app_id}: {e}")
                continue
        
        return apps_data
    
    def search_apps(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for apps in the App Store"""
        logger.info(f"Searching for apps with query: '{query}'")
        
        try:
            url = f"{self.base_url}/search"
            querystring = {"term": query, "limit": limit}
            
            response = requests.get(url, headers=self.headers, params=querystring)
            
            if response.status_code == 200:
                results = response.json()
                return [self._normalize_appstore_data(app) for app in results.get('results', [])]
            else:
                logger.error(f"Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching apps: {e}")
            return []
    
    def _normalize_appstore_data(self, app_data: Dict) -> Dict:
        """Normalize App Store API response to match our schema"""
        normalized = {
            'app_name': app_data.get('trackName', ''),
            'category': app_data.get('primaryGenreName', ''),
            'rating': app_data.get('averageUserRating', np.nan),
            'review_count': app_data.get('userRatingCount', 0),
            'price_usd': app_data.get('price', 0.0),
            'is_free': app_data.get('price', 0.0) == 0.0,
            'content_rating': app_data.get('contentAdvisoryRating', ''),
            'description': app_data.get('description', ''),
            'developer': app_data.get('artistName', ''),
            'app_id': app_data.get('trackId', ''),
            'data_source': 'app_store',
            'processed_date': datetime.now().isoformat()
        }
        
        return normalized

def create_unified_schema(kaggle_data: pd.DataFrame, appstore_data: List[Dict]) -> pd.DataFrame:
    """Combine Kaggle and App Store data into unified schema"""
    logger.info("Creating unified data schema...")
    
    # Convert App Store data to DataFrame
    if appstore_data:
        appstore_df = pd.DataFrame(appstore_data)
    else:
        # Create empty DataFrame with expected columns
        appstore_df = pd.DataFrame(columns=[
            'app_name', 'category', 'rating', 'review_count', 'price_usd', 
            'is_free', 'content_rating', 'description', 'developer', 
            'app_id', 'data_source', 'processed_date'
        ])
    
    # Ensure both DataFrames have consistent columns
    common_columns = [
        'app_name', 'category', 'rating', 'review_count', 'price_usd',
        'is_free', 'content_rating', 'data_source', 'processed_date'
    ]
    
    # Prepare Kaggle data
    kaggle_subset = kaggle_data.reindex(columns=common_columns, fill_value=np.nan)
    
    # Prepare App Store data
    appstore_subset = appstore_df.reindex(columns=common_columns, fill_value=np.nan)
    
    # Combine datasets
    combined_df = pd.concat([kaggle_subset, appstore_subset], ignore_index=True)
    
    # Add unified features
    combined_df['has_rating'] = combined_df['rating'].notna()
    combined_df['rating_tier'] = pd.cut(
        combined_df['rating'], 
        bins=[0, 2, 3, 4, 5], 
        labels=['Poor', 'Fair', 'Good', 'Excellent'],
        include_lowest=True
    )
    
    combined_df['review_tier'] = pd.cut(
        combined_df['review_count'],
        bins=[0, 100, 1000, 10000, float('inf')],
        labels=['Low', 'Medium', 'High', 'Very High'],
        include_lowest=True
    )
    
    logger.info(f"Unified dataset created with {len(combined_df)} apps")
    logger.info(f"Data sources: {combined_df['data_source'].value_counts().to_dict()}")
    
    return combined_df

if __name__ == "__main__":
    # Example usage
    pipeline = DataPipeline()
    
    # This would be run after downloading the Kaggle dataset
    # df = pipeline.load_kaggle_data('data/raw/googleplaystore.csv')
    # cleaned_df = pipeline.clean_kaggle_data()
    # cleaned_df.to_csv('data/processed/cleaned_kaggle_data.csv', index=False)
    
    print("Data pipeline module ready!")
