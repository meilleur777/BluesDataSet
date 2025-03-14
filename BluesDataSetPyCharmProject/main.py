# main.py - Main script to run the scrapers
from scrapers import wikipedia, musicbrainz, discogs
import utils
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    print("Starting scraping process...")

    data_wikipedia = wikipedia.scrape()
    utils.save_to_txt(data_wikipedia, "Scrap_Result/scraped_wikipedia.txt")

    data_musicbrainz = musicbrainz.scrape()
    utils.save_to_txt(data_musicbrainz, "Scrap_Result/scraped_musicbrainz.txt")

    data_discogs = discogs.scrape()
    utils.save_to_txt(data_discogs, "Scrap_Result/scraped_discogs.txt")

    print("Scraping complete. Data saved.")


if __name__ == "__main__":
    main()

# List of Source Sites
# 1. Wikipedia: https://en.wikipedia.org/wiki/List_of_blues_musicians
# 2. MusicBrainz: https://musicbrainz.org/
# 3. Discogs: https://www.discogs.com/