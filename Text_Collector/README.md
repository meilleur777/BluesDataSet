# Blues Artist Data Collector

This project collects and processes information about blues artists from various sources. It extracts artist names and URLs from CSV files, consolidates them, and then scrapes web pages to gather information about the artists' influences, careers, and styles.

## Project Structure

```
blues-artist-data/
├── blues_data/                # Input directory for CSV files (empty in repository)
│   └── .gitkeep               # Empty file to ensure directory is tracked in git
├── artist_data/               # Output directory for scraped content
├── main.py                    # Main script to run the full pipeline
├── process_csv.py             # Script to process CSV files
├── scrape_artists.py          # Script to scrape artist information from websites
├── discogs_collector.py       # Script to collect artist information from Discogs API
├── discogs_oauth_client.py    # Discogs OAuth implementation
├── artist_urls.csv            # Consolidated artist URLs
├── requirements.txt           # Required Python packages
├── .env.example               # Example environment variables file
└── README.md                  # This file
```

## Features

- Identifies and processes CSV files containing artist or musician data in the `blues_data` folder
- Extracts unique artist names and their corresponding URLs
- Creates a consolidated CSV file linking artists to their URLs
- Scrapes web content from the URLs to gather information about:
  - Biography
  - Life
  - Career
  - Musical style
  - Influences (who influenced the artist and who they influenced)
  - Legacy and impact
  - Technique and approach
- Integrates with the Discogs API to collect detailed artist information
- Saves the scraped content as text files organized by artist

## Requirements

- Python 3.7+
- Required packages:
  - pandas
  - requests
  - beautifulsoup4
  - python-dotenv
  - urllib3

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/blues-artist-data.git
   cd blues-artist-data
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. The empty `blues_data` directory is already included in the repository (maintained with a `.gitkeep` file).

4. Setup Discogs API credentials (optional, for accessing Discogs data):
   - Copy `.env.example` to `.env`
   - Register an application on the [Discogs Developer Settings](https://www.discogs.com/settings/developers)
   - Fill in your Discogs Consumer Key and Consumer Secret in the `.env` file

## Usage

1. Place your CSV files containing artist data in the `blues_data` directory. The files should have names containing "artist" or "musician".

2. Run the complete pipeline with a single command:
   ```
   python main.py
   ```
   This will:
   - Process the CSV files
   - Scrape artist information from websites
   - If `.env` is configured, process Discogs URLs using the API

   Alternatively, you can run each step separately:
   ```
   python process_csv.py         # Process CSV files only
   python scrape_artists.py      # Scrape artist information from websites only
   python discogs_collector.py   # Process Discogs URLs only (requires .env configuration)
   ```

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
   - The program searches for CSV files in the `blues_data` directory that have "artist" or "musician" in their names
   - It attempts to identify columns containing artist names and URLs
   - It consolidates this information into a single CSV file

2. **Web Scraping**:
   - For each artist, the program visits the associated URLs (excluding Discogs URLs)
   - It searches for content related to biography, life, career, style, etc.
   - It specifically looks for information about influences and impact
   - The relevant content is saved as text files in artist-specific directories

3. **Discogs API Integration**:
   - For Discogs URLs, the program extracts the artist ID
   - It uses the Discogs API to retrieve detailed artist information
   - The first time you run it, you'll need to authorize the application
   - After authorization, the OAuth tokens are saved for future use

## Customization

You can customize the categories of information to scrape by modifying the `categories` list in `scrape_artists.py`. The current categories include:
- biography
- life
- career
- style
- history
- music
- influence
- legacy
- impact
- development
- technique
- genre
- contribution
- background

## Notes

- The web scraping script includes a delay between requests to avoid overwhelming servers
- The script attempts to identify content specifically related to the artist's influences
- The scraped text includes the source URL for reference
- Special characters in artist names (like quotes) are handled properly
- Discogs URLs are processed separately using their official API

