# Blues Artists Web Scraper

A comprehensive data collection tool for blues music researchers, historians, and enthusiasts. This application gathers detailed information about blues artists from multiple authoritative sources, creating a rich dataset that can be used for research, analysis, and discovery of blues music heritage.

## Overview

This project aims to solve the challenge of collecting dispersed blues artist information by aggregating data from multiple authoritative sources into a single, structured dataset. The resulting data provides a more complete picture of artists' careers, influences, and contributions to the blues genre.

## Features

- **Multi-source data collection**: Aggregates artist information from leading music databases, APIs, and websites
- **Comprehensive artist profiles**: Collects biographical details, discographies, styles, and historical context
- **Intelligent data merging**: Combines data from different sources with deduplication and conflict resolution
- **Modular architecture**: Easily extensible with new data sources through standardized scraper interfaces
- **Responsible API usage**: Implements proper rate limiting, authentication, and respects usage policies
- **Structured output**: Provides data in both CSV and JSON formats for flexibility in downstream analysis

## Data Sources

| Source | Description | Data Provided | API Required | Rate Limits |
|--------|-------------|---------------|--------------|-------------|
| **Wikipedia** | Web scraping of the List of Blues Musicians page | Names, birth/death years, origins, primary styles | No | Reasonable request frequency |
| **Discogs** | Music database with comprehensive release information | Detailed artist info, discographies, styles, genres | Yes (OAuth) | 60 requests/min (authenticated) |
| **MusicBrainz** | Open music encyclopedia with structured data | Artist relationships, recordings, aliases | Yes* | 1 request/sec |

\* *MusicBrainz requires providing application information but doesn't require a token*

## Project Structure

```
BluesDataSet/
├── .env                  # Environment variables (API keys, etc.)
├── .env.example          # Example/template for the .env file
├── .gitignore            # Git ignore file
├── README.md             # Project documentation
├── requirements.txt      # Project dependencies
├── main.py               # Entry point for the application
└── scrapers/
    ├── __init__.py       # Makes the directory a package
    ├── base.py           # Base scraper class with common functionality
    ├── wikipedia.py      # Wikipedia scraper implementation
    ├── discogs.py        # Discogs API scraper implementation
    ├── oauth_client.py   # Discogs OAuth authentication handler
    ├── musicbrainz.py    # MusicBrainz API scraper implementation
    └── utils.py          # Utility functions for data processing
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/BluesDataSet.git
   cd BluesDataSet
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up API credentials:
   - **Discogs**: Register at [Discogs Developers](https://www.discogs.com/settings/developers) to get your API key
   - **MusicBrainz**: Follow [MusicBrainz guidelines](https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting) for API usage

5. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials using a text editor
   ```

## Usage

### Command Line

Run the main script to scrape data from all sources:

```bash
python main.py
```

Optional arguments:
```bash
python main.py --output-dir=my_data  # Specify output directory
python main.py --sources=wikipedia,discogs  # Only run specific scrapers
python main.py --pages=3  # Limit number of pages scraped (where applicable)
```

### Python API

Import the application in your own code:

```python
from main import BluesScraperApp

# Initialize the scraper
app = BluesScraperApp(output_dir="my_data")

# List all available sources
sources = app.list_sources()
print(f"Available sources: {sources}")

# Run a specific scraper
wikipedia_data = app.run_scraper("wikipedia")
print(f"Collected {len(wikipedia_data)} artists from Wikipedia")

# Run all scrapers and merge results
all_artists = app.run_all_scrapers()
print(f"Total unique artists collected: {len(all_artists)}")

# Access artist data
for artist in all_artists.head(5).itertuples():
    print(f"Name: {artist.name}, Born: {artist.birth_year}, Style: {artist.primary_style}")
```

## Output Files

The scraper creates several output files in the specified directory:

| Filename | Format | Description |
|----------|--------|-------------|
| `discogs_checkpoint.json` | JSON | Incremental scraping progress for resuming interrupted runs |
| `discogs_blues_albums.csv/.json` | CSV/JSON | Album information from Discogs including genres, styles, and artists |
| `discogs_blues_artists.csv/.json` | CSV/JSON | Artist information from Discogs including profiles and releases |
| `wikipedia_blues_musicians.csv` | CSV | Basic artist information extracted from Wikipedia |
| `musicbrainz_blues_musicians.csv` | CSV | Artist data from the MusicBrainz database |

## Legal and Ethical Considerations

- Always check each website's robots.txt file and terms of service before scraping
- Implement reasonable delays between requests to avoid overloading servers
- Use the data for personal research purposes only, respecting copyright restrictions
- Consider reaching out to website administrators for permission if using data commercially
- Be aware that some data may be subject to copyright or other intellectual property rights
