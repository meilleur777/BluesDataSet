#!/usr/bin/env python
"""
Main script to run the complete blues artist data collection pipeline.
This script executes the CSV processing, web scraping, and Discogs API phases.
"""

import os
import sys
import time
from process_csv import main as process_csv_main
from scrape_artists import main as scrape_artists_main

def check_prerequisites():
    """Check if the required directories exist."""
    if not os.path.exists('blues_data'):
        os.makedirs('blues_data')
        print("Created 'blues_data' directory. Please place your CSV files there.")
        return False
    
    # Check if there are any files in the blues_data directory
    files = [f for f in os.listdir('blues_data') if os.path.isfile(os.path.join('blues_data', f))]
    if not files:
        print("Warning: No files found in 'blues_data' directory.")
        print("Please add your CSV files containing artist data to the 'blues_data' directory.")
        return False
    
    return True

def main():
    """Run the complete data collection pipeline."""
    print("\n" + "=" * 60)
    print("BLUES ARTIST DATA COLLECTION PIPELINE")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPrerequisites not met. Please address the issues above and try again.")
        return
    
    try:
        # Create artist_data directory if it doesn't exist
        if not os.path.exists('artist_data'):
            os.makedirs('artist_data')
        
        # Phase 1: Process CSV files
        print("\n--- PHASE 1: PROCESSING CSV FILES ---")
        process_csv_main()
        
        # Check if the consolidated CSV was created
        if not os.path.exists('artist_urls.csv'):
            print("\nError: The consolidated artist URLs file was not created.")
            print("Please check the logs above for errors.")
            return
        
        print("\nPhase 1 completed successfully.")
        print("Pausing for 2 seconds before starting web scraping...")
        time.sleep(2)
        
        # Phase 2: Scrape artist information from regular websites
        print("\n--- PHASE 2: SCRAPING ARTIST INFORMATION FROM WEBSITES ---")
        try:
            scrape_artists_main()
            print("\nWebsite scraping completed successfully.")
        except Exception as e:
            print(f"\n\nError during website scraping phase: {str(e)}")
            print("Some artist data may have been collected before the error occurred.")
        
        # Phase 3: Process Discogs URLs if .env file exists
        if os.path.exists('.env'):
            print("\n--- PHASE 3: PROCESSING DISCOGS URLS ---")
            try:
                from discogs_collector import process_discogs_urls
                process_discogs_urls()
                print("\nDiscogs processing completed successfully.")
            except ImportError:
                print("\nError: discogs_oauth_client.py not found or could not be imported.")
                print("Make sure the discogs_oauth_client.py file is in the same directory.")
            except Exception as e:
                print(f"\n\nError during Discogs processing: {str(e)}")
                print("To process Discogs URLs, make sure you have the required API credentials in .env file.")
        else:
            print("\nSkipping Discogs processing - .env file not found.")
            print("To process Discogs URLs, create a .env file with your Discogs API credentials.")
            print("You can use .env.example as a template.")
        
        print("\nData collection pipeline completed.")
        print("Check the 'artist_data' directory for the scraped content.")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nAn error occurred: {str(e)}")
        print("The data collection pipeline could not be completed.")
        sys.exit(1)

if __name__ == "__main__":
    main()