# scrapers/base.py - Base scraper class with artist name listing

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

    def save_data(self, data, filename):
        """Save data to CSV file"""
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)

        if data.empty:
            print(f"No data to save for {self.source_name}")
            return data

        # Fix complex types before saving to CSV
        for column in data.columns:
            # Convert list columns to string representation
            if data[column].apply(lambda x: isinstance(x, list)).any():
                data[column] = data[column].apply(
                    lambda x: ', '.join(x) if isinstance(x, list) else x
                )

        filepath = os.path.join(self.output_dir, filename)
        data.to_csv(filepath, index=False)
        print(f"Saved {len(data)} records to {filepath}")

        return data

    def save_as_text(self, data, filename):
        """
        Save a list of artist names to text file

        Args:
            data: List of dictionaries or DataFrame with artist data
            filename: Output filename
        """
        if isinstance(data, pd.DataFrame):
            artists = data.to_dict('records')
        else:
            artists = data

        if not artists:
            print(f"No data to save as text for {self.source_name}")
            return

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{self.source_name} Blues Artists\n")
            f.write(f"{'=' * len(self.source_name)} {'=' * 14}\n\n")
            f.write(f"Total Artists: {len(artists)}\n\n")

            # Write a simple list of artist names
            f.write("Artist Names:\n")
            for i, artist in enumerate(sorted(artists, key=lambda x: x.get('name', '').lower()), 1):
                f.write(f"{i}. {artist.get('name', 'Unknown Artist')}\n")

        print(f"Saved artist names to {filepath}")

    @abstractmethod
    def scrape(self, **kwargs):
        """
        Main scraping method to be implemented by subclasses

        Returns:
            DataFrame of scraped data
        """
        pass