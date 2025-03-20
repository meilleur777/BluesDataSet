# scrapers/utils.py
import time
from datetime import datetime, timedelta


class ScraperProgress:
    """Tracks and displays text-based progress for multiple scrapers"""

    def __init__(self, scrapers):
        """
        Initialize with list of scrapers

        Args:
            scrapers: Dictionary of scraper names and instances
        """
        self.scrapers = scrapers
        self.total_count = len(scrapers)
        self.completed = 0
        self.current_scraper = None
        self.start_time = None
        self.scraper_start_time = None

        # Track status of each scraper
        self.status = {name: "Pending" for name in scrapers.keys()}

        # Track artist counts
        self.artist_counts = {name: 0 for name in scrapers.keys()}

    def start(self):
        """Start the progress tracking"""
        self.start_time = time.time()
        self.print_header()

    def start_scraper(self, name):
        """
        Mark a scraper as started

        Args:
            name: Name of the scraper
        """
        self.current_scraper = name
        self.scraper_start_time = time.time()
        self.status[name] = "Running"
        print(f"Starting {name} scraper...")

    def complete_scraper(self, name, artist_count=0):
        """
        Mark a scraper as completed

        Args:
            name: Name of the scraper
            artist_count: Number of artists scraped
        """
        self.status[name] = "Completed"
        self.artist_counts[name] = artist_count
        self.completed += 1
        self.current_scraper = None

        # Calculate elapsed time for this scraper
        elapsed = time.time() - self.scraper_start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        print(f"Completed {name} scraper: Found {artist_count} artists in {elapsed_str}")

        # Calculate overall progress
        overall_percent = (self.completed / self.total_count) * 100
        overall_elapsed = time.time() - self.start_time
        overall_elapsed_str = str(timedelta(seconds=int(overall_elapsed)))

        print(
            f"Overall progress: {self.completed}/{self.total_count} scrapers ({overall_percent:.1f}%) - Elapsed: {overall_elapsed_str}")

    def fail_scraper(self, name, error_message):
        """
        Mark a scraper as failed

        Args:
            name: Name of the scraper
            error_message: Error message
        """
        self.status[name] = f"Failed: {error_message}"
        self.completed += 1
        self.current_scraper = None

        # Calculate elapsed time for this scraper
        elapsed = time.time() - self.scraper_start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        print(f"Failed {name} scraper after {elapsed_str}: {error_message}")

        # Calculate overall progress
        overall_percent = (self.completed / self.total_count) * 100
        overall_elapsed = time.time() - self.start_time
        overall_elapsed_str = str(timedelta(seconds=int(overall_elapsed)))

        print(
            f"Overall progress: {self.completed}/{self.total_count} scrapers ({overall_percent:.1f}%) - Elapsed: {overall_elapsed_str}")

    def print_header(self):
        """Print the header for the progress tracking"""
        print("\n" + "=" * 80)
        print(f"Blues Artist Scraper - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print(f"Processing {self.total_count} scrapers: {', '.join(self.scrapers.keys())}")
        print("-" * 80)

    def finish(self):
        """Complete the progress tracking and show summary"""
        # Show the final summary
        print("\n" + "=" * 80)
        print("Scraping Summary")
        print("=" * 80)

        total_artists = sum(self.artist_counts.values())
        total_time = time.time() - self.start_time
        time_str = str(timedelta(seconds=int(total_time)))

        successful = sum(1 for status in self.status.values() if status == "Completed")

        print(f"Total scrapers: {self.total_count}")
        print(f"Successful: {successful}")
        print(f"Failed: {self.total_count - successful}")
        print(f"Total artists collected: {total_artists}")
        print(f"Total time: {time_str}")
        print("=" * 80)

        # Show detailed results
        print("\nDetailed Results:")
        for name, status in self.status.items():
            status_symbol = "✓" if status == "Completed" else "✗"
            artist_count = self.artist_counts[name]
            print(f"  {status_symbol} {name:15}: {artist_count:4} artists - {status}")
        print()