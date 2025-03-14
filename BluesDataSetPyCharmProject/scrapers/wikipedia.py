# scrapers/wikipedia.py - Wikipedia Scraper
import requests
from bs4 import BeautifulSoup

def scrape():
    """
    Scrapes the list of blues musicians from Wikipedia.
    Extracts artist names from the relevant category section on the Wikipedia page.
    Returns a list of musician names.
    """
    url = "https://en.wikipedia.org/wiki/List_of_blues_musicians"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    musicians = []
    for li in soup.select(".mw-category-group ul li a"):
        musicians.append(li.text)

    return musicians
