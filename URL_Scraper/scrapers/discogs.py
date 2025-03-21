import os
import json
import time
import random
import string
import requests
import pandas as pd
import dotenv
from .base import BaseScraper


class DiscogsScraper(BaseScraper):
    """Scraper for Discogs API focusing on collecting blues artist names and URLs only"""

    def __init__(self, output_dir="blues_data", env_file=".env"):
        super().__init__(output_dir)
        self.api_url = "https://api.discogs.com"
        self.source_name = "Discogs"

        # Load environment variables
        dotenv.load_dotenv(env_file)

        # Set user agent
        self.user_agent = os.getenv("DISCOGS_USER_AGENT")
        if not self.user_agent:
            self.user_agent = "BluesDataSet/1.0 +https://github.com/yourusername/BluesDataSet"

        self.headers["User-Agent"] = self.user_agent

        # Try to load existing OAuth tokens
        self.oauth_token = os.getenv("DISCOGS_OAUTH_TOKEN")
        self.oauth_token_secret = os.getenv("DISCOGS_OAUTH_TOKEN_SECRET")
        self.consumer_key = os.getenv("DISCOGS_CONSUMER_KEY")
        self.consumer_secret = os.getenv("DISCOGS_CONSUMER_SECRET")

        # Rate limiting settings
        self.requests_per_minute = 40  # Conservative rate limit (official limit is 60)
        self.request_timestamps = []

        # If we don't have OAuth tokens but have consumer credentials, authenticate
        if (not self.oauth_token or not self.oauth_token_secret) and (self.consumer_key and self.consumer_secret):
            self.authenticate()
        elif self.oauth_token and self.oauth_token_secret and self.consumer_key and self.consumer_secret:
            print("Using existing OAuth tokens for authentication")
        else:
            # Fall back to token-based authentication if no OAuth credentials
            self.token = os.getenv("DISCOGS_TOKEN")
            if self.token:
                self.headers["Authorization"] = f"Discogs token={self.token}"
                print("Using personal access token for authentication (limited access)")
                # Lower rate limit for token authentication
                self.requests_per_minute = 25
            else:
                print("WARNING: No authentication credentials found. API access will be very limited.")
                # Lower rate limit for unauthenticated requests
                self.requests_per_minute = 20

    def authenticate(self):
        """Run the OAuth authentication flow"""
        print("No OAuth tokens found. Starting authentication process...")
        from .oauth_client import DiscogsOAuthClient
        oauth_client = DiscogsOAuthClient()
        result = oauth_client.complete_oauth_flow()

        # Save the tokens for future use
        self.oauth_token = result['oauth_token']
        self.oauth_token_secret = result['oauth_token_secret']

        print("\nAdd these lines to your key.env file to skip authentication next time:")
        print(f"DISCOGS_OAUTH_TOKEN={self.oauth_token}")
        print(f"DISCOGS_OAUTH_TOKEN_SECRET={self.oauth_token_secret}")

    def enforce_rate_limit(self):
        """
        Advanced rate limiting that respects Discogs API limits
        Ensures we don't exceed requests_per_minute
        """
        current_time = time.time()

        # Remove timestamps older than 1 minute
        self.request_timestamps = [t for t in self.request_timestamps if current_time - t < 60]

        # If we've reached the limit, wait until we can make another request
        if len(self.request_timestamps) >= self.requests_per_minute:
            # Calculate the time we need to wait
            oldest_timestamp = min(self.request_timestamps)
            wait_time = 60 - (current_time - oldest_timestamp) + 1  # Add 1 second buffer

            if wait_time > 0:
                print(f"\nRate limit reached. Waiting {wait_time:.1f} seconds before continuing...")
                time.sleep(wait_time)
                # Clear old timestamps after waiting
                self.request_timestamps = []

        # Add current request timestamp
        self.request_timestamps.append(time.time())

    def make_request(self, url, params=None, method="GET", max_retries=3):
        """
        Make an HTTP request to the Discogs API with OAuth authentication
        and advanced rate limiting + retry logic
        """
        retry_count = 0
        response = None

        while retry_count < max_retries:
            try:
                # Enforce rate limiting before making the request
                self.enforce_rate_limit()

                if hasattr(self, 'oauth_token') and hasattr(self, 'oauth_token_secret'):
                    # Use OAuth for authentication
                    oauth_timestamp = str(int(time.time()))
                    oauth_nonce = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))

                    # Create Authorization header with exact format required
                    auth_header = (
                        'OAuth oauth_consumer_key="' + self.consumer_key + '", '
                        'oauth_nonce="' + oauth_nonce + '", '
                        'oauth_token="' + self.oauth_token + '", '
                        'oauth_signature="' + self.consumer_secret + '&' + self.oauth_token_secret + '", '
                        'oauth_signature_method="PLAINTEXT", '
                        'oauth_timestamp="' + oauth_timestamp + '"'
                    )

                    headers = {
                        'Authorization': auth_header,
                        'User-Agent': self.user_agent
                    }

                    if method.upper() == "GET":
                        response = requests.get(url, headers=headers, params=params)
                    elif method.upper() == "POST":
                        response = requests.post(url, headers=headers, data=params)
                    else:
                        response = requests.request(method, url, headers=headers, data=params)
                else:
                    # Use regular request with header-based authentication
                    return super().make_request(url, params, method)

                # Handle rate limiting response
                if response.status_code == 429:
                    retry_count += 1

                    # Get retry-after header if available, otherwise use exponential backoff
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        wait_time = int(retry_after)
                    else:
                        wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8...

                    print(f"\nRate limit exceeded (429). Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                    continue

                # Handle server errors
                elif 500 <= response.status_code < 600:
                    retry_count += 1
                    wait_time = 2 ** retry_count
                    print(f"\nServer error ({response.status_code}). Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                    continue

                # Raise error for other non-success status codes
                response.raise_for_status()
                return response

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                print(f"\nConnection error: {e}. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                time.sleep(wait_time)

            except Exception as e:
                # Re-raise other exceptions
                print(f"\nError during request: {e}")
                raise

        # If we've exhausted retries
        if response:
            raise Exception(f"Maximum retries ({max_retries}) exceeded. Last status code: {response.status_code}")
        else:
            raise Exception(f"Maximum retries ({max_retries}) exceeded without successful response")

    def search_artists(self, query="blues", pages=3):
        """
        Search directly for blues artists by name - simpler approach than album search
        
        Args:
            query: Search term (default: "blues")
            pages: Number of search result pages to process
            
        Returns:
            List of artist dictionaries with name and URL
        """
        artists = []
        artist_ids = set()  # To avoid duplicates
        
        print(f"Searching Discogs for '{query}' artists...")
        
        for page in range(1, pages + 1):
            try:
                # Search for blues artists directly
                params = {
                    "q": query,
                    "type": "artist",
                    "per_page": 100,
                    "page": page
                }
                
                print(f"Processing artist search page {page}/{pages}...")
                
                response = self.make_request(
                    url=f"{self.api_url}/database/search",
                    params=params
                )
                
                data = response.json()
                results = data.get("results", [])
                
                # Process each artist result
                for result in results:
                    try:
                        # Make sure it's an artist
                        if result.get("type") != "artist":
                            continue
                            
                        artist_id = result.get("id")
                        title = result.get("title", "")
                        
                        # Skip if we've already processed this artist
                        if artist_id in artist_ids:
                            continue
                            
                        artist_ids.add(artist_id)
                        
                        # Create artist info with name and URL only
                        artist_info = {
                            "name": title,
                            "url": f"https://www.discogs.com/artist/{artist_id}"
                        }
                        
                        artists.append(artist_info)
                        print(".", end="", flush=True)
                        
                    except Exception as e:
                        print(f"\nError processing artist result: {str(e)}")
                
                print("")  # New line after the progress dots
                
                # Check if we've reached the last page
                pagination = data.get("pagination", {})
                if page >= pagination.get("pages", 0):
                    print(f"\nReached the last page of results ({page})")
                    break
                    
            except Exception as e:
                print(f"\nError fetching Discogs artist search page {page}: {str(e)}")
        
        print(f"Found {len(artists)} artists from Discogs search")
        return artists

    def scrape(self, search_term="blues", pages=3):
        """
        Main scraping method that collects blues artist names and URLs from Discogs
        
        Args:
            search_term: Search term (default: "blues")
            pages: Number of search result pages to process
            
        Returns:
            DataFrame containing artist names and URLs
        """
        # Search directly for artists - simpler approach
        artists = self.search_artists(query=search_term, pages=pages)
        
        # Convert to DataFrame
        df = pd.DataFrame(artists)
        
        if df.empty:
            print("No artist data collected from Discogs")
            return pd.DataFrame()
            
        # Ensure we only have name and URL columns
        if 'name' in df.columns and 'url' in df.columns:
            return df[['name', 'url']]
        else:
            print("Warning: Required columns missing from Discogs results")
            return df
