# Blues Artists URL Collector

A focused data collection tool for blues music researchers, historians, and enthusiasts. This application gathers URLs associated with blues artists from authoritative sources, creating a streamlined dataset that can be used for further research and analysis.

## Overview

This project aims to solve the challenge of collecting dispersed blues artist information by aggregating basic artist data (names and URLs) from multiple authoritative sources into a single, structured dataset. The resulting data provides the foundation for deeper research into artists' careers, influences, and contributions to the blues genre.

## Features

- **Multi-source data collection**: Aggregates artist names and URLs from leading music databases and websites
- **Simple, focused output**: Collects only essential identification information (name and URL)
- **Modular architecture**: Easily extensible with new data sources through standardized scraper interfaces
- **Responsible API usage**: Implements proper rate limiting, authentication, and respects usage policies
- **Structured output**: Provides data in both CSV and JSON formats for flexibility in downstream analysis

## Data Sources

| Source | Description | Data Provided | API Required | Rate Limits |
|--------|-------------|---------------|--------------|-------------|
| **Wikipedia** | Web scraping of the List of Blues Musicians page | Names and URLs to artist pages | No | Reasonable request frequency |
| **Discogs** | Music database with comprehensive release information | Artist names and URLs | Yes (OAuth) | 60 requests/min (authenticated) |

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

## Output Files

The scraper creates several output files in the specified directory:

| Filename | Format | Description |
|----------|--------|-------------|
| `discogs_checkpoint.json` | JSON | Incremental scraping progress for resuming interrupted runs |
| `discogs_blues_artists.csv/.json` | CSV/JSON | Artist names and URLs from Discogs |
| `wikipedia_blues_musicians.csv` | CSV | Artist names and URLs extracted from Wikipedia |
| `blues_artists_combined.csv` | CSV | Combined dataset of all artist names and URLs from all sources |

## Legal and Ethical Considerations

- Always check each website's robots.txt file and terms of service before scraping
- Implement reasonable delays between requests to avoid overloading servers
- Use the data for personal research purposes only, respecting copyright restrictions
- Consider reaching out to website administrators for permission if using data commercially
