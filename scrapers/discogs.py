import os
import json
import time
import random
import string
import requests
import pandas as pd
from collections import defaultdict
import dotenv
from .base import BaseScraper


class DiscogsScraper(BaseScraper):
    """Scraper for Discogs API focusing on blues albums to find artists"""

    def __init__(self, output_dir="blues_data", env_file="key.env"):
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

        Args:
            url: URL to request
            params: Query parameters
            method: HTTP method (GET, POST, etc.)
            max_retries: Maximum number of retries on rate limit or server errors

        Returns:
            Response object
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

                    print(
                        f"\nRate limit exceeded (429). Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                    continue

                # Handle server errors
                elif 500 <= response.status_code < 600:
                    retry_count += 1
                    wait_time = 2 ** retry_count
                    print(
                        f"\nServer error ({response.status_code}). Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                    continue

                # Raise error for other non-success status codes
                response.raise_for_status()
                return response

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                print(
                    f"\nConnection error: {e}. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
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

    def scrape(self, pages=5, per_page=100, allow_checkpointing=True):
        """
        Search for top blues albums on Discogs and extract artists

        Args:
            pages: Number of pages of albums to retrieve
            per_page: Results per page
            allow_checkpointing: Whether to save progress after each page

        Returns:
            DataFrame of artists
        """
        print("Searching Discogs for top blues albums...")

        # This will store all unique artists we find
        artist_ids = set()
        artists_data = []
        albums_data = []

        # Checkpoint file
        checkpoint_file = os.path.join(self.output_dir, "discogs_checkpoint.json")
        start_page = 1

        # Try to load checkpoint if enabled
        if allow_checkpointing and os.path.exists(checkpoint_file):
            try:
                with open(checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                    if 'artists' in checkpoint and 'albums' in checkpoint and 'last_page' in checkpoint:
                        artists_data = checkpoint['artists']
                        albums_data = checkpoint['albums']
                        artist_ids = set(artist['discogs_id'] for artist in artists_data)
                        start_page = checkpoint['last_page'] + 1
                        print(
                            f"Resuming from checkpoint: {len(artists_data)} artists and {len(albums_data)} albums collected, starting at page {start_page}")
            except Exception as e:
                print(f"Error loading checkpoint: {e}")

        # Album search loop
        for page in range(start_page, pages + 1):
            try:
                # Search for blues albums
                params = {
                    "q": "blues",
                    "type": "master",  # Master releases (canonical albums)
                    "genre": "Blues",
                    "per_page": per_page,
                    "page": page,
                    "sort": "have,desc"  # Sort by popularity (number of people who have it)
                }

                print(f"Processing album page {page}/{pages}...")

                response = self.make_request(
                    url=f"{self.api_url}/database/search",
                    params=params
                )

                data = response.json()
                results = data.get("results", [])

                # Process each album
                page_albums = []
                for result in results:
                    try:
                        # Only process masters
                        if result.get("type") != "master":
                            continue

                        album_id = result.get("id")
                        if not album_id:
                            continue

                        # Get album details
                        album_data = self.get_album_details(album_id)
                        if album_data:
                            page_albums.append(album_data)

                            # Extract artist information from album
                            if "artists" in album_data:
                                for artist in album_data["artists"]:
                                    # Only process new artists we haven't seen yet
                                    artist_id = artist.get("id")
                                    if artist_id and artist_id not in artist_ids:
                                        artist_ids.add(artist_id)
                                        print(f"+", end="", flush=True)

                                        # Get detailed artist info
                                        artist_data = self.get_artist_details(artist_id)
                                        if artist_data:
                                            artists_data.append(artist_data)

                            print(".", end="", flush=True)

                    except Exception as e:
                        print(f"\nError processing Discogs album: {e}")

                # Add albums from this page
                albums_data.extend(page_albums)

                # Save checkpoint after each page
                if allow_checkpointing:
                    with open(checkpoint_file, 'w') as f:
                        json.dump({
                            'artists': artists_data,
                            'albums': albums_data,
                            'last_page': page,
                            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                        }, f, default=str)
                    print(
                        f"\nSaved checkpoint after page {page}: {len(artists_data)} artists and {len(albums_data)} albums collected so far")

                # Check if we've reached the last page
                pagination = data.get("pagination", {})
                if page >= pagination.get("pages", 0):
                    print(f"\nReached the last page of results ({page})")
                    break

                print("")  # New line after dots

            except Exception as e:
                print(f"Error fetching Discogs album search page {page}: {e}")
                # Don't exit, try next page

        # Save both artists and albums data
        print(f"\nCollected data for {len(artists_data)} blues artists from {len(albums_data)} albums")
        self.save_data(albums_data, "discogs_blues_albums.csv")
        return self.save_data(artists_data, "discogs_blues_artists.csv")

    def get_album_details(self, master_id):
        """
        Get detailed album information from Discogs

        Args:
            master_id: Discogs master release ID

        Returns:
            Album data dictionary
        """
        try:
            response = self.make_request(
                url=f"{self.api_url}/masters/{master_id}"
            )

            master = response.json()

            # Check if the album has blues in genres or styles
            genres = master.get("genres", [])
            styles = master.get("styles", [])

            # Only include albums with blues in their genres or styles
            blues_related = any(
                "blues" in genre.lower() for genre in genres
            ) or any(
                "blues" in style.lower() for style in styles
            )

            if not blues_related:
                return None

            # Extract artists
            artists_data = []
            for artist in master.get("artists", []):
                artist_info = {
                    "id": artist.get("id"),
                    "name": artist.get("name"),
                    "role": artist.get("role", "Main")
                }
                artists_data.append(artist_info)

            # Extract relevant data
            album_data = {
                "title": master.get("title"),
                "discogs_id": master.get("id"),
                "url": master.get("uri"),
                "year": master.get("year"),
                "genres": genres,
                "styles": styles,
                "artists": artists_data,
                "tracklist": master.get("tracklist", []),
                "source": "Discogs"
            }

            return album_data

        except Exception as e:
            print(f"\nError getting Discogs album details for ID {master_id}: {e}")
            return None

    def get_artist_details(self, artist_id):
        """
        Get detailed artist information from Discogs

        Args:
            artist_id: Discogs artist ID

        Returns:
            Artist data dictionary
        """
        try:
            response = self.make_request(
                url=f"{self.api_url}/artists/{artist_id}"
            )

            artist = response.json()

            # Get releases for this artist (up to 3 releases)
            releases_data = self.get_artist_releases(artist_id, limit=3)

            # Extract relevant data
            artist_data = {
                "name": artist.get("name"),
                "discogs_id": artist.get("id"),
                "url": artist.get("uri"),
                "profile": artist.get("profile"),
                "genres": artist.get("genres", []),
                "styles": artist.get("styles", []),
                "releases_count": artist.get("releases_count", 0),
                "top_releases": releases_data,
                "source": "Discogs"
            }

            return artist_data

        except Exception as e:
            print(f"\nError getting Discogs artist details for ID {artist_id}: {e}")
            return None

    def get_artist_releases(self, artist_id, limit=3):
        """
        Get artist's releases from Discogs

        Args:
            artist_id: Discogs artist ID
            limit: Maximum number of releases to retrieve

        Returns:
            List of release dictionaries
        """
        try:
            params = {
                "sort": "year",
                "sort_order": "desc",
                "per_page": limit,
                "page": 1
            }

            response = self.make_request(
                url=f"{self.api_url}/artists/{artist_id}/releases",
                params=params
            )

            data = response.json()
            releases = data.get("releases", [])

            # Extract relevant release information
            release_data = []
            for release in releases:
                release_info = {
                    "title": release.get("title"),
                    "year": release.get("year"),
                    "type": release.get("type"),
                    "role": release.get("role")
                }
                release_data.append(release_info)

            return release_data

        except Exception as e:
            print(f"\nError getting Discogs releases for artist ID {artist_id}: {e}")
            return []

    def save_data(self, data, filename):
        """
        Save data to both CSV and JSON files

        Args:
            data: Data to save
            filename: Base filename (without extension)

        Returns:
            DataFrame of saved data
        """
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)

        if data.empty:
            print(f"No data to save for {self.source_name}")
            return data

        # Save as CSV with basic columns
        csv_safe_data = data.copy()

        # Convert complex columns to strings
        for col in csv_safe_data.columns:
            if csv_safe_data[col].apply(lambda x: isinstance(x, (list, dict))).any():
                csv_safe_data[col] = csv_safe_data[col].apply(
                    lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x
                )

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Save CSV
        csv_path = os.path.join(self.output_dir, filename)
        csv_safe_data.to_csv(csv_path, index=False)
        print(f"Saved {len(data)} records to {csv_path}")

        # Save full data as JSON to preserve complex structures
        json_path = os.path.join(self.output_dir, filename.replace('.csv', '.json'))
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(
                data.to_dict('records'),
                f,
                ensure_ascii=False,
                default=str,
                indent=2
            )
        print(f"Saved complete data to {json_path}")

        return data