import requests
import pandas as pd
from bs4 import BeautifulSoup
from .base import BaseScraper


class WikipediaScraper(BaseScraper):
    def __init__(self, output_dir="blues_data"):
        super().__init__(output_dir)
        self.url = "https://en.wikipedia.org/wiki/List_of_blues_musicians"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.source_name = "Wikipedia"

    def scrape(self):
        """
        Scrape blues musicians data from Wikipedia and return as a DataFrame.
        Each row contains only Name and URL.
        """
        try:
            # Fetch the webpage
            response = requests.get(self.url, headers=self.headers)

            # Check if the request was successful
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all tables with the specified class
            tables = soup.find_all('table', class_='wikitable sortable plainrowheaders')

            if not tables:
                print("No tables found with the specified class. The page structure might have changed.")
                return pd.DataFrame()

            # Initialize a list to store all musician data
            all_musicians = []

            # Process each table
            for table in tables:
                # Get all rows except the header row
                rows = table.find_all('tr')[1:]  # Skip the header row

                # Process each row
                for row in rows:
                    # Extract the musician's name from the <a> tag inside the <th> element
                    name_element = row.find('th')
                    if name_element:
                        # Get the name specifically from the <a> tag inside the <th>
                        name_a_tag = name_element.find('a')
                        if name_a_tag:
                            name = name_a_tag.text.strip()
                            # Get the href attribute and create the full URL
                            wiki_path = name_a_tag.get('href', '')
                            if wiki_path.startswith('/wiki/'):
                                full_url = f"https://en.wikipedia.org{wiki_path}"
                            else:
                                full_url = ""
                            
                            # Create a musician data dictionary with only name and URL
                            musician_data = {
                                'name': name,
                                'url': full_url
                            }
                            
                            # Add the musician to our list
                            all_musicians.append(musician_data)

            # Convert list to DataFrame
            musicians_df = pd.DataFrame(all_musicians)

            # Return the DataFrame with only name and URL columns
            if not musicians_df.empty:
                print(f"Collected {len(musicians_df)} blues musicians from Wikipedia")
                return musicians_df[['name', 'url']]
            else:
                print("No musician data found on Wikipedia.")
                return pd.DataFrame()

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the Wikipedia webpage: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"An error occurred while scraping Wikipedia: {e}")
            return pd.DataFrame()
