# scrapers/discogs.py
import os
import json
import pandas as pd
from .base import BaseScraper


class DiscogsScraper(BaseScraper):
    """Scraper for Discogs API using standard requests library"""

    def __init__(self, output_dir="blues_data"):
        super().__init__(output_dir)
        self.api_url = "https://api.discogs.com"
        self.token = os.getenv("DISCOGS_TOKEN")

        # Add token and user agent to headers if available
        if self.token:
            self.headers["Authorization"] = f"Discogs token={self.token}"

        # Discogs requires a user agent with contact information
        self.headers["User-Agent"] = os.getenv(
            "DISCOGS_USER_AGENT",
            "BluesDataSet/1.0 +https://github.com/yourusername/BluesDataSet"
        )

    def scrape(self, pages=5, per_page=100):
        """
        Search for blues artists on Discogs

        Args:
            pages: Number of pages to retrieve
            per_page: Results per page

        Returns:
            DataFrame of artists
        """
        if not self.token:
            print("WARNING: DISCOGS_TOKEN not found in environment variables. Results will be limited.")
            print("To obtain a token, register at https://www.discogs.com/settings/developers")

        print("Searching Discogs for blues artists...")
        artists = []

        for page in range(1, pages + 1):
            try:
                # Search for blues artists
                params = {
                    "q": "blues",
                    "type": "artist",
                    "per_page": per_page,
                    "page": page
                }

                print(f"Processing page {page}/{pages}...")

                response = self.make_request(
                    url=f"{self.api_url}/database/search",
                    params=params
                )

                data = response.json()
                results = data.get("results", [])

                for result in results:
                    try:
                        artist_id = result.get("id")
                        if not artist_id:
                            continue

                        # Get detailed artist info
                        artist_data = self.get_artist_details(artist_id)
                        if artist_data:
                            artists.append(artist_data)
                            print(".", end="", flush=True)

                    except Exception as e:
                        print(f"\nError processing Discogs artist: {e}")

                # Check if we've reached the last page
                pagination = data.get("pagination", {})
                if page >= pagination.get("pages", 0):
                    print(f"\nReached the last page of results ({page})")
                    break

                # Rate limiting - Discogs allows 60 requests per minute for authenticated requests
                self.rate_limit(1, 2)

                print("")  # New line after dots

            except Exception as e:
                print(f"Error fetching Discogs search page {page}: {e}")

        print(f"\nCollected data for {len(artists)} blues artists from Discogs")
        return self.save_data(artists, "discogs_blues_artists.csv")

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

            # Check if artist has blues in their genres
            genres = artist.get("genres", [])
            styles = artist.get("styles", [])

            # Only include artists with blues in their genres or styles
            blues_related = any(
                "blues" in genre.lower() for genre in genres
            ) or any(
                "blues" in style.lower() for style in styles
            )

            if not blues_related:
                return None

            # Get releases for this artist (up to 3 releases)
            releases_data = self.get_artist_releases(artist_id, limit=3)

            # Extract relevant data
            artist_data = {
                "name": artist.get("name"),
                "discogs_id": artist.get("id"),
                "url": artist.get("uri"),
                "profile": artist.get("profile"),
                "genres": genres,
                "styles": styles,
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

            # Rate limiting
            self.rate_limit(1, 2)

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