import requests
import time
import pandas as pd
from .base import BaseScraper


class MusicBrainzScraper(BaseScraper):
    def __init__(self, output_dir="blues_data"):
        super().__init__(output_dir)

        # MusicBrainz API base URL
        self.base_url = "https://musicbrainz.org/ws/2"

        # Set proper user agent as required by MusicBrainz API
        # Replace with your own application name and contact information
        self.headers = {
            'User-Agent': 'BluesMusiciansScraper/1.0 (your-email@example.com)',
            'Accept': 'application/json'
        }

        # Define the search parameters for blues musicians
        self.query_params = {
            'query': 'tag:blues AND type:person',
            'limit': 100,  # API allows max 100 per request
            'fmt': 'json'
        }

    def scrape(self, max_artists=500):
        """
        Scrape blues musicians data from MusicBrainz API and return as a list of dictionaries.
        Limited to a specified number of artists.

        Args:
            max_artists: Maximum number of artists to retrieve (default: 500)

        Returns:
            pandas.DataFrame: DataFrame containing artist information
        """
        try:
            print(f"Starting MusicBrainz data scraping (limited to {max_artists} artists)...")
            musicians = []

            # Initial API endpoint for artist search
            endpoint = f"{self.base_url}/artist"

            # Track pagination
            offset = 0
            total_count = 0

            # Continue fetching until we reach the max_artists limit
            while total_count < max_artists:
                # Update offset for pagination
                self.query_params['offset'] = offset

                # Make the API request
                response = requests.get(endpoint, headers=self.headers, params=self.query_params)

                # Check if the request was successful
                response.raise_for_status()

                # Parse the response as JSON
                data = response.json()

                # Get artists from the response
                artists = data.get('artists', [])

                # If no more artists or empty response, break the loop
                if not artists:
                    break

                # Process each artist in the response
                for artist in artists:
                    if total_count >= max_artists:
                        break

                    # Extract basic artist information
                    artist_id = artist.get('id', '')
                    name = artist.get('name', '')

                    # Construct the URL to the artist's MusicBrainz page
                    url = f"https://musicbrainz.org/artist/{artist_id}"

                    # Extract additional details
                    gender = artist.get('gender', '')
                    country = artist.get('country', '')

                    # Extract life span information
                    life_span = artist.get('life-span', {})
                    birthday = life_span.get('begin', '')
                    deathday = life_span.get('end', '')

                    # Create musician data dictionary
                    musician_data = {
                        'name': name,
                        'id': artist_id,
                        'url': url,
                        'gender': gender,
                        'country': country,
                        'birthday': birthday,
                        'deathday': deathday,
                        'source': 'musicbrainz'
                    }

                    # Add to our musicians list
                    musicians.append(musician_data)
                    total_count += 1

                # Update offset for next page
                offset += len(artists)

                # Respect MusicBrainz rate limiting (1 request per second)
                time.sleep(1)

                print(f"Retrieved {total_count} artists so far...")

            # Convert to DataFrame
            df = pd.DataFrame(musicians)

            # Save the data using the parent class's save_data function
            if not df.empty:
                csv_filename = 'musicbrainz_blues_musicians.csv'
                df.to_csv(f"{self.output_dir}/{csv_filename}", index=False)
                print(f"Data saved to '{csv_filename}'")
            else:
                print("No musician data found.")

            # Return the DataFrame for further processing
            return df

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from MusicBrainz API: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"An error occurred: {e}")
            return pd.DataFrame()

    def save_as_text(self, df, filename):
        """Save artist data as a formatted text file"""
        if df is None or df.empty:
            return

        with open(f"{self.output_dir}/{filename}", 'w', encoding='utf-8') as f:
            f.write(f"Blues Artists from MusicBrainz\n")
            f.write(f"===========================\n\n")
            f.write(f"Total Artists: {len(df)}\n\n")

            # List all artist names alphabetically
            f.write("Artist Names:\n")
            sorted_artists = sorted(df['name'].tolist())
            for i, name in enumerate(sorted_artists, 1):
                f.write(f"{i}. {name}\n")

        print(f"Saved artist list to '{filename}'")

    def run(self):
        """Main method to execute the scraping process"""
        print("Starting to scrape MusicBrainz for Blues musicians data (limited to 500 artists)...")
        df = self.scrape(max_artists=500)
        print(f"Scraping completed. {len(df)} musicians found.")
        return df


# If this script is run directly, execute the scraper
if __name__ == "__main__":
    musicbrainz_scraper = MusicBrainzScraper()
    musicbrainz_scraper.run()