# Blues Artists Web Scraper

A data collection tool for blues music researchers and enthusiasts. This application gathers information about blues artists from multiple authoritative sources.

## Features

- Multi-source data collection from leading music databases and websites
- Structured modular architecture for easy maintenance and extension
- API integrations with proper rate limiting and error handling
- Data deduplication and merging capabilities
- Artist information including biographies, discographies, and musical styles

## Data Sources

| Source | URL | Type | API Required |
|--------|-----|------|-------------|
| Wikipedia | https://en.wikipedia.org/wiki/List_of_blues_musicians | Web Scraping | No |
| Discogs | https://www.discogs.com/ | API | Yes |
| MusicBrainz | https://musicbrainz.org/ | API | Yes* |

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
    ├── base.py           # Base scraper class
    ├── wikipedia.py      # Wikipedia scraper
    ├── discogs.py        # Discogs API scraper
    ├── musicbrainz.py    # MusicBrainz API scraper
    └── utils.py          # Utility functions for scraping/processing
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/BluesDataSet.git
   cd BluesDataSet
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your API credentials
   ```

## Usage

Run the main script to scrape data from all sources:

```
python main.py
```

Or import the application in your own code:

```python
from main import BluesScraperApp

# Initialize the scraper
app = BluesScraperApp(output_dir="my_data")

# List all available sources
app.list_sources()

# Run a specific scraper
wikipedia_data = app.run_scraper("wikipedia")

# Run all scrapers and merge results
all_artists = app.run_all_scrapers()
```

## Output Files

The scraper creates several output files in the specified directory:

1. **CSV files**: Contains structured data for each artist
   - `wikipedia_blues_artists.csv`
   - `discogs_blues_artists.csv`
   - `musicbrainz_blues_artists.csv`
   - `all_blues_artists.csv` (combined data from all sources)

2. **Text files**: Simple text listing of artist names
   - `wikipedia_blues_artists.txt`
   - `discogs_blues_artists.txt`
   - `musicbrainz_blues_artists.txt`
   - `all_blues_artists.txt` (combined list from all sources)

3. **JSON files**: Complete data with complex structures preserved
   - `wikipedia_blues_artists.json`
   - `discogs_blues_artists.json`
   - `musicbrainz_blues_artists.json`
   - `all_blues_artists.json` (combined data from all sources)

## Legal and Ethical Considerations

- Always check each website's robots.txt file and terms of service before scraping
- Implement reasonable delays between requests to avoid overloading servers
- Use the data for personal research purposes only, respecting copyright restrictions
- Consider reaching out to website administrators for permission if using data commercially

## License

This project is licensed under the MIT License - see the LICENSE file for details.