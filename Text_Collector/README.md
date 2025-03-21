# Text Collector

This project collects and processes information about blues artists from various sources. It extracts text data from URLs, consolidates them, and organizes the information by artist.

## Project Structure

```
Text_Collector/
├── input_data/               # Input directory for CSV files
│   └── .gitkeep              # Empty file to ensure directory is tracked in git
├── blues_artist_data/        # Output directory for scraped content
├── main.py                   # Main script to run the full pipeline
├── process_csv.py            # Script to process CSV files
├── scrape_artists.py         # Script to scrape artist information from websites
├── wikipedia_collector.py    # Script to collect artist information from Wikipedia
├── discogs_collector.py      # Script to collect artist information from Discogs API
├── discogs_oauth_client.py   # Discogs OAuth implementation
├── sanitizer.py              # Text and filename sanitization utilities
├── requirements.txt          # Required Python packages
├── .env.example              # Example environment variables file
└── README.md                 # This file
```

## Features

- Processes the artist_urls.csv file containing artist names and their corresponding URLs
- Extracts content from multiple sources for each artist:
  - Wikipedia pages (saved as name_wikipedia.txt)
  - Discogs artist profiles (saved as name_discogs.txt) 
  - Other web sources (saved as name_web.txt)
- Focuses on gathering information about:
  - Biography
  - Life
  - Career
  - Musical style
  - Influences (who influenced the artist and who they influenced)
  - Legacy and impact
  - Technique and approach
- Integrates with the Discogs API to collect detailed artist information
- Saves the scraped content as separate text files organized by artist
- Applies thorough text sanitization to ensure clean output files

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/blues-artist-data.git
   cd blues-artist-data/Text_Collector
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. The sample `input_data` directory is already included in the repository (maintained with a `.gitkeep` file). You can add any .csv file that contains name and corressponding url.

4. Setup Discogs API credentials (optional, for accessing Discogs data):
   - Copy `.env.example` to `.env`
   - Register an application on the [Discogs Developer Settings](https://www.discogs.com/settings/developers)
   - Fill in your Discogs Consumer Key and Consumer Secret in the `.env` file

## Usage

1. Place the artist_urls.csv file (generated from URL_Scraper) in the `input_data` directory.

2. Run the complete pipeline with a single command:
   ```
   python main.py
   ```
   This will:
   - Process the artist_urls.csv file
   - Collect information from Wikipedia pages
   - Scrape artist information from other websites
   - If `.env` is configured, process Discogs URLs using the API

## Output Structure

For each artist, the program creates:
1. A directory with the sanitized artist name
2. Inside that directory, up to three text files:
   - `{artist_name}_wikipedia.txt` - Content from Wikipedia
   - `{artist_name}_discogs.txt` - Content from Discogs
   - `{artist_name}_web.txt` - Content from other websites

## Handling Discogs URLs

The program handles Discogs URLs differently from other websites:

1. Regular website scraping won't work with Discogs due to their anti-scraping measures
2. Instead, the program uses the Discogs API to collect artist information
3. To use this feature, you need to:
   - Register an application with Discogs
   - Configure your credentials in the `.env` file
   - The first time you run the program with Discogs URLs, it will guide you through the OAuth authentication process

## How It Works

1. **CSV Processing**:
   - The program reads the artist_urls.csv file from the input_data directory
   - It extracts artist names and URLs for processing

2. **Wikipedia Collection**:
   - For URLs containing "wikipedia.org", the program uses a specialized collector
   - It extracts structured content including basic information, sections, and categories
   - It specifically identifies content related to influences and musical impact

3. **Web Scraping**:
   - For other web URLs (excluding Discogs), the program searches for content related to biography, style, etc.
   - It specifically looks for information about influences and impact
   - The relevant content is saved as text files in artist-specific directories

4. **Discogs API Integration**:
   - For Discogs URLs, the program extracts the artist ID
   - It uses the Discogs API to retrieve detailed artist information
   - The first time you run it, you'll need to authorize the application
   - After authorization, the OAuth tokens are saved for future use

## Text Sanitization

All text content is sanitized before being saved:
- Non-breaking spaces (`\xa0`) are converted to regular spaces
- Other invisible Unicode characters are removed
- Whitespace is normalized
- HTML tags can be optionally removed
- Filenames are sanitized to remove invalid characters

## Notes

- The web scraping script includes a delay between requests to avoid overwhelming servers
- Special characters in artist names are handled properly through the sanitizer
- Discogs URLs are processed separately using their official API
