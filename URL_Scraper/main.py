# main.py - Simplified application that produces a single CSV output

import os
import pandas as pd
from dotenv import load_dotenv
from scrapers.wikipedia import WikipediaScraper
from scrapers.discogs import DiscogsScraper
from scrapers.utils import ScraperProgress

# Load environment variables
load_dotenv()


class BluesScraperApp:
    """Main application class for orchestrating blues artist URL collection"""

    def __init__(self, output_dir="blues_data", output_filename="artist_urls.csv"):
        """Initialize the scraper application with output directory"""
        self.output_dir = output_dir
        self.output_filename = output_filename

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize scrapers - MusicBrainz removed
        self.scrapers = {
            'wikipedia': WikipediaScraper(output_dir),
            'discogs': DiscogsScraper(output_dir)
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
            
            # Filter to only include name and url columns
            if df is not None and not df.empty:
                # Ensure we only keep name and url columns, and drop the rest
                required_columns = ['name', 'url']
                existing_columns = df.columns.tolist()
                
                # Check if the required columns exist
                for col in required_columns:
                    if col not in existing_columns:
                        print(f"Warning: Column '{col}' not found in {source_name} results")
                        if col == 'name' and 'artist' in existing_columns:
                            df['name'] = df['artist']  # Use 'artist' column as fallback for name
                        elif col == 'url' and 'link' in existing_columns:
                            df['url'] = df['link']  # Use 'link' column as fallback for url
                
                # Filter columns to only include name and url
                columns_to_keep = [col for col in required_columns if col in df.columns]
                if len(columns_to_keep) < len(required_columns):
                    missing = set(required_columns) - set(columns_to_keep)
                    print(f"Warning: Missing required columns in {source_name} results: {missing}")
                
                df = df[columns_to_keep]

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
                df = self.run_scraper(name)  # Use run_scraper to properly filter columns

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
            merged_df = self.merge_data(results)
            
            # Save the single output file
            output_path = os.path.join(self.output_dir, self.output_filename)
            merged_df.to_csv(output_path, index=False)
            print(f"Saved combined artist data to {output_path}")
            
            return merged_df
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
        if not results:
            return pd.DataFrame()

        # Combine all dataframes
        merged_df = pd.concat(results, ignore_index=True)
        
        # Remove duplicates based on name (case-insensitive)
        merged_df['name_lower'] = merged_df['name'].str.lower()
        merged_df = merged_df.drop_duplicates(subset=['name_lower'])
        merged_df = merged_df.drop(columns=['name_lower'])
        
        return merged_df


if __name__ == "__main__":
    app = BluesScraperApp()

    # Print list of sources
    app.list_sources()

    # Check for environment variables and warn if missing
    if not os.getenv("DISCOGS_TOKEN"):
        print("\nWARNING: DISCOGS_TOKEN not found in environment variables.")
        print("The Discogs scraper will run with limited functionality.")
        print("Consider creating a .env file based on .env.example.")

    # Run all scrapers with progress tracking
    print("\nStarting data collection process...")
    all_artists = app.run_all_scrapers()

    if all_artists is not None:
        print(f"\nCompleted scraping with {len(all_artists)} unique blues artists.")
        print(f"Data saved to '{os.path.join(app.output_dir, app.output_filename)}'")
    else:
        print("\nFailed to collect data from any sources.")
        print("Please check the error messages above and fix the issues before continuing.")
