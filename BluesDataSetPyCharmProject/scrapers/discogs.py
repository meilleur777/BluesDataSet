# scrapers/discogs.py - Discogs Scraper
import requests
import os

def scrape():
    """
    Fetches a list of blues musicians from the Discogs API.
    Returns a list of artist names tagged with 'blues'.
    Requires a Discogs API key set as an environment variable: DISCOGS_API_KEY
    """
    api_key = os.getenv("DISCOGS_API_KEY")
    if not api_key:
        print("Error: Discogs API key not found. Please set the DISCOGS_API_KEY environment variable.")
        return []

    url = "https://api.discogs.com/database/search"
    headers = {"User-Agent": "BluesScraper/1.0", "Authorization": f"Discogs token={api_key}"}
    params = {
        "q": "blues",
        "type": "artist",
        "per_page": 100,
        "page": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        musicians = [result["title"] for result in data.get("results", [])]
        return musicians
    except Exception as e:
        print(f"Error while scraping Discogs: {e}")
        return []
