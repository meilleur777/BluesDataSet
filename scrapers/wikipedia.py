import requests
from bs4 import BeautifulSoup
from .base import BaseScraper  # Importing the correct base class


class WikipediaScraper(BaseScraper):
    def __init__(self, output_dir="blues_data"):
        super().__init__(output_dir)
        self.url = "https://en.wikipedia.org/wiki/List_of_blues_musicians"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape(self):
        """
        Scrape blues musicians data from Wikipedia and return as a list of dictionaries.
        Each dictionary contains Name, Birth_Year, Death_Year, Origin, Primary_Style, and References.
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
                return []

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
                        else:
                            continue  # Skip if no <a> tag found as per requirements

                        # Extract all td elements for the additional data
                        data_cells = row.find_all('td')

                        # Initialize variables for data extraction
                        birth_year = death_year = origin = primary_style = ""

                        # Extract data based on the number of cells
                        if len(data_cells) >= 1:
                            birth_year = data_cells[0].text.strip()
                        if len(data_cells) >= 2:
                            death_year = data_cells[1].text.strip()
                        if len(data_cells) >= 3:
                            origin = data_cells[2].text.strip()
                        if len(data_cells) >= 4:
                            primary_style = data_cells[3].text.strip()

                        # Create a musician data dictionary
                        musician_data = {
                            'Name': name,
                            'URL': full_url,
                            'Birth_Year': birth_year,
                            'Death_Year': death_year,
                            'Origin': origin,
                            'Primary_Style': primary_style
                        }

                        # Add the musician to our list
                        all_musicians.append(musician_data)

            # Save the data using the parent class's save_data function
            if all_musicians:
                self.save_data(all_musicians, 'wikipedia_blues_musicians.csv')
                print(f"Data saved to 'wikipedia_blues_musicians.csv'")
            else:
                print("No musician data found.")

            # Return the data for potential further processing
            return all_musicians

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the webpage: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def run(self):
        """Main method to execute the scraping process"""
        print("Starting to scrape Wikipedia for Blues musicians data...")
        musicians = self.scrape()
        print(f"Scraping completed. {len(musicians)} musicians found.")


# If this script is run directly, execute the scraper
if __name__ == "__main__":
    scraper = WikipediaScraper()
    scraper.run()