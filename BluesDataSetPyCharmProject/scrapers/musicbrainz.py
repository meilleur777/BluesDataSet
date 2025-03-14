# scrapers/musicbrainz.py - MusicBrainz Scraper
import requests

def scrape():
    """
    Fetch a list of up to 100 blues musicians from the MusicBrainz API.
    Returns a list of artist names tagged with 'blues'.
    """
    url = "https://musicbrainz.org/ws/2/artist/?query=tag:blues&fmt=json&limit=100"
    response = requests.get(url)
    data = response.json()

    musicians = [artist.get("name", "Unknown") for artist in data.get("artists", [])]
    return musicians
