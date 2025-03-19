# main.py - Simplified application with only Discogs active

import os
import pandas as pd
import json
from dotenv import load_dotenv
from scrapers.wikipedia import WikipediaScraper
from scrapers.discogs import DiscogsScraper
from scrapers.musicbrainz import MusicBrainzScraper
from scrapers.utils import ScraperProgress

# Load environment variables
load_dotenv()


class BluesScraperApp:
    """Main application class for orchestrating blues artist data collection"""

    def __init__(self, output_dir="blues_data"):
        """Initialize the scraper application with output directory"""
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize scrapers - only Discogs active
        self.scrapers = {
            'wikipedia': WikipediaScraper(output_dir),
            'discogs': DiscogsScraper(output_dir),
            'musicbrainz': MusicBrainzScraper(output_dir)
        }

    def list_sources(self):
        """Print a list of all data sources being used"""
        print("\n=== Blues Artist Data Sources ===")
        sources = [
            {
                "name": "Wikipedia",
                "url": "https://en.wikipedia.org/wiki/List_of_blues_musicians",
                "api_required": False,
                "description": "Encyclopedia with lists of blues musicians categorized by instrument"
            },
            {
                "name": "Discogs",
                "url": "https://www.discogs.com/",
                "api_required": True,
                "description": "Database and marketplace for music recordings with detailed artist and release information"
            },
            {
                "name": "MusicBrainz",
                "url": "https://musicbrainz.org/",
                "api_required": True,
                "description": "Open music encyclopedia with structured data on artists, releases, and recordings"
            }
        ]

        for source in sources:
            print(f"\n{source['name']}")
            print(f"URL: {source['url']}")
            print(f"API Required: {'Yes' if source['api_required'] else 'No'}")
            print(f"Description: {source['description']}")

        return sources

    def run_scraper(self, source_name, **kwargs):
        """Run a specific scraper by name"""
        if source_name not in self.scrapers:
            raise ValueError(f"Unknown scraper: {source_name}")

        print(f"\nRunning {source_name} scraper...")
        try:
            df = self.scrapers[source_name].scrape(**kwargs)

            # Also save summary text file
            if df is not None and not df.empty:
                text_filename = f"{source_name.lower()}_blues_artists.txt"
                self.scrapers[source_name].save_as_text(df, text_filename)

                # Also save complete data to JSON to preserve all fields
                json_filepath = f"{self.output_dir}/{source_name.lower()}_blues_artists.json"
                with open(json_filepath, 'w', encoding='utf-8') as f:
                    records = []
                    for record in df.to_dict('records'):
                        for key, value in record.items():
                            if isinstance(value, list):
                                record[key] = ', '.join(value)
                        records.append(record)
                    json.dump(records, f, indent=2, ensure_ascii=False)
                print(f"Saved complete data to {json_filepath}")

            return df
        except Exception as e:
            print(f"Error running {source_name} scraper: {e}")
            print(f"Detailed error: {str(e)}")
            return None

    def run_all_scrapers(self, skip=None):
        """
        Run all scrapers and merge results with simple progress tracking

        Args:
            skip: List of scraper names to skip

        Returns:
            DataFrame of merged results
        """
        skip = skip or []
        active_scrapers = {name: scraper for name, scraper in self.scrapers.items()
                           if name not in skip}

        # Initialize the progress tracker
        progress = ScraperProgress(active_scrapers)
        progress.start()

        results = []

        for name, scraper in active_scrapers.items():
            try:
                progress.start_scraper(name)
                df = scraper.scrape()

                if df is not None and not df.empty:
                    results.append(df)
                    progress.complete_scraper(name, len(df))
                else:
                    progress.complete_scraper(name, 0)

            except Exception as e:
                progress.fail_scraper(name, str(e))
                print(f"Error running {name} scraper: {e}")

        # Finalize progress display
        progress.finish()

        if results:
            return self.merge_data(results)
        else:
            print("No data collected from any source.")
            return None

    def merge_data(self, results):
        """
        Merge data from different sources into a single DataFrame

        Args:
            results: List of DataFrames from different sources

        Returns:
            Merged DataFrame
        """
        import json

        if not results:
            return pd.DataFrame()

        # Combine all dataframes
        merged_df = pd.concat(results, ignore_index=True)

        # Handle list columns - convert to strings for better readability
        for column in merged_df.columns:
            if merged_df[column].apply(lambda x: isinstance(x, list)).any():
                merged_df[column] = merged_df[column].apply(
                    lambda x: self.process_list_data(x) if isinstance(x, list) else x
                )

        return merged_df

    def process_list_data(self, data):
        """
        Process list data based on its content

        Args:
            data: List of data

        Returns:
            String representation of the list
        """
        if not data:
            return ""

        # Check if the list contains dictionaries
        if any(isinstance(item, dict) for item in data):
            # For lists containing dictionaries, convert to JSON string
            import json
            return json.dumps(data)

        # For simple lists of strings or other simple types, join with commas
        return ', '.join(str(item) for item in data)

if __name__ == "__main__":
    app = BluesScraperApp()

    # Print list of sources
    app.list_sources()

    # Check for environment variables and warn if missing - uncommented Discogs check
    if not os.getenv("DISCOGS_TOKEN"):
        print("\nWARNING: DISCOGS_TOKEN not found in environment variables.")
        print("The Discogs scraper will run with limited functionality.")
        print("Consider creating a .env file based on .env.example.")

    # Run all scrapers with progress tracking
    print("\nStarting data collection process...")
    all_artists = app.run_all_scrapers()

    if all_artists is not None:
        print(f"\nCompleted scraping with {len(all_artists)} total unique blues artists.")
        print(f"Data saved to the '{app.output_dir}' directory.")
    else:
        print("\nFailed to collect data from any sources.")
        print("Please check the error messages above and fix the issues before continuing.")