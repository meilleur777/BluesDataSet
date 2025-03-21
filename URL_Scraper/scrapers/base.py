# scrapers/base.py - Simplified base scraper class

import os
import time
import random
import requests
import pandas as pd
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Base class for all scrapers with common functionality"""

    def __init__(self, output_dir="blues_data"):
        """Initialize with common configurations"""
        self.output_dir = output_dir
        self.source_name = self.__class__.__name__.replace('Scraper', '')

        # Standard headers for web requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def make_request(self, url, method="GET", params=None, data=None, json=None, retry_count=3, retry_delay=5):
        """
        Make a request with retry logic

        Args:
            url: URL to request
            method: HTTP method
            params: Query parameters
            data: Form data
            json: JSON data
            retry_count: Number of retries
            retry_delay: Delay between retries in seconds

        Returns:
            Response object
        """
        for attempt in range(retry_count):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    data=data,
                    json=json,
                    timeout=30
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < retry_count - 1:
                    sleep_time = retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Request failed: {e}. Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    print(f"Request failed after {retry_count} attempts: {e}")
                    raise

    def rate_limit(self, min_delay=1, max_delay=3):
        """Implement rate limiting between requests"""
        time.sleep(random.uniform(min_delay, max_delay))

    def save_data(self, data, filename=None):
        """
        Save only name and URL fields for artists/musicians
        
        Note: This method is simplified to match the project requirement changes
              but individual scrapers don't save files directly anymore.
              The main application now handles saving the combined file.
        """
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)

        if data.empty:
            print(f"No data to save for {self.source_name}")
            return data

        # Ensure we only have name and URL columns
        columns_to_keep = []
        
        # Handle name column
        if 'name' in data.columns:
            columns_to_keep.append('name')
        elif 'artist' in data.columns:
            data['name'] = data['artist']
            columns_to_keep.append('name')
        
        # Handle URL column
        if 'url' in data.columns:
            columns_to_keep.append('url')
        elif 'link' in data.columns:
            data['url'] = data['link']
            columns_to_keep.append('url')
        
        # Filter to only keep name and URL
        if columns_to_keep:
            data = data[columns_to_keep]
        
        # Print status but don't save the file (main app will save the combined file)
        print(f"Collected {len(data)} artist records from {self.source_name}")

        return data

    @abstractmethod
    def scrape(self, **kwargs):
        """
        Main scraping method to be implemented by subclasses

        Returns:
            DataFrame of scraped data with name and URL columns
        """
        pass
