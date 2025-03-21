"""
Wikipedia Collector for the Blues Artist Data Collector project.

This module collects and processes data from Wikipedia pages for blues artists.
It extracts biographical information, influences, career details, and other
relevant content from Wikipedia pages and saves it in a structured format.
"""

import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
from sanitizer import sanitize_text, sanitize_filename, sanitize_file_content


def is_wikipedia_url(url):
    """
    Check if the URL is from Wikipedia
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if it's a Wikipedia URL, False otherwise
    """
    return "wikipedia.org" in url.lower()


def extract_wikipedia_title(url):
    """
    Extract the title/page name from a Wikipedia URL
    
    Args:
        url (str): Wikipedia URL
        
    Returns:
        str: The title of the Wikipedia page
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Handle different Wikipedia URL formats
    if '/wiki/' in path:
        # Standard format: https://en.wikipedia.org/wiki/Muddy_Waters
        title = path.split('/wiki/')[-1]
    elif '/w/index.php' in path:
        # Query format: https://en.wikipedia.org/w/index.php?title=Muddy_Waters
        query = parsed_url.query
        query_params = dict(param.split('=') for param in query.split('&'))
        title = query_params.get('title', '')
    else:
        # Unknown format, return empty string
        return ''
    
    # Convert URL encoding to human-readable format
    from urllib.parse import unquote
    title = unquote(title)
    
    # Replace underscores with spaces (Wikipedia convention)
    title = title.replace('_', ' ')
    
    return title


def get_wikipedia_content(url):
    """
    Scrape content from a Wikipedia page
    
    Args:
        url (str): URL of the Wikipedia page
        
    Returns:
        dict: Dictionary containing extracted content
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.select('table, .sidebar, .ambox, .navbox, .reference, .mw-editsection'):
            element.extract()
        
        # Get the page title
        page_title = soup.select_one('h1#firstHeading')
        page_title = page_title.text.strip() if page_title else extract_wikipedia_title(url)
        
        # Extract basic information
        basic_info = {}
        infobox = soup.select_one('.infobox')
        if infobox:
            for row in infobox.select('tr'):
                header = row.select_one('th')
                data = row.select_one('td')
                if header and data:
                    key = header.text.strip()
                    value = data.text.strip()
                    basic_info[key] = value
        
        # Extract the main content sections
        sections = {}
        current_section = 'Introduction'
        
        # Get the main content div
        content_div = soup.select_one('#mw-content-text')
        if not content_div:
            return {
                'title': page_title,
                'basic_info': basic_info,
                'content': {},
                'url': url
            }
        
        # Process elements sequentially to group paragraphs under their respective sections
        section_paragraphs = []
        
        # Find elements that are direct children of the content div
        for element in content_div.select('p, h2, h3'):
            if element.name in ['h2', 'h3']:
                # Save previous section
                if section_paragraphs:
                    sections[current_section] = '\n\n'.join(section_paragraphs)
                    section_paragraphs = []
                
                # Start new section
                section_title = element.text.strip()
                # Remove edit links
                section_title = re.sub(r'\[\w+\]', '', section_title)
                section_title = section_title.strip()
                
                if section_title:
                    current_section = section_title
            
            elif element.name == 'p' and element.text.strip():
                # Add paragraph to current section
                clean_text = sanitize_text(element.text)
                if clean_text:
                    section_paragraphs.append(clean_text)
        
        # Save the last section
        if section_paragraphs:
            sections[current_section] = '\n\n'.join(section_paragraphs)
        
        # Extract categories
        categories = []
        category_links = soup.select('.mw-normal-catlinks ul li a')
        for link in category_links:
            categories.append(link.text.strip())
        
        # Identify influence-related content
        influence_keywords = [
            "influence", "influenced", "inspiration", "inspired", 
            "mentor", "teacher", "student", "follow", "admire",
            "style", "technique", "approach", "method", "sound",
            "impact", "legacy", "contribution", "innovate", "pioneer"
        ]
        
        influences = []
        for section_name, section_content in sections.items():
            # Check if section name indicates influence
            if any(keyword in section_name.lower() for keyword in influence_keywords):
                influences.append(f"FROM SECTION '{section_name}':\n{section_content}")
            else:
                # Otherwise search for influence keywords in the content
                paragraphs = section_content.split('\n\n')
                for paragraph in paragraphs:
                    if any(keyword in paragraph.lower() for keyword in influence_keywords):
                        influences.append(f"FROM SECTION '{section_name}':\n{paragraph}")
        
        return {
            'title': page_title,
            'basic_info': basic_info,
            'content': sections,
            'categories': categories,
            'influences': influences,
            'url': url
        }
        
    except Exception as e:
        print(f"Error scraping Wikipedia page {url}: {str(e)}")
        return {
            'title': extract_wikipedia_title(url),
            'basic_info': {},
            'content': {},
            'categories': [],
            'influences': [],
            'url': url,
            'error': str(e)
        }


def format_wikipedia_content(content):
    """
    Format Wikipedia content for output
    
    Args:
        content (dict): Dictionary with Wikipedia content
        
    Returns:
        str: Formatted content for text file
    """
    output = []
    
    # Add artist name/title
    output.append(f"ARTIST: {content['title']}")
    output.append("")
    
    # Add basic info if available
    if content['basic_info']:
        output.append("BASIC INFORMATION:")
        for key, value in content['basic_info'].items():
            output.append(f"{key}: {value}")
        output.append("")
    
    # Add sections of interest first if they exist
    sections_of_interest = ['Biography', 'Life', 'Career', 'Style', 'Music', 'Influences']
    for section in sections_of_interest:
        if section in content['content']:
            output.append(f"{section.upper()}:")
            output.append(content['content'][section])
            output.append("")
    
    # Add influence-specific content
    if content['influences']:
        output.append("INFLUENCES AND IMPACT:")
        for influence_content in content['influences']:
            output.append(influence_content)
            output.append("")
    
    # Add other sections that weren't covered above
    for section, text in content['content'].items():
        if section != 'Introduction' and section not in sections_of_interest:
            output.append(f"{section.upper()}:")
            output.append(text)
            output.append("")
    
    # Add introduction last (if it exists)
    if 'Introduction' in content['content']:
        output.append("INTRODUCTION:")
        output.append(content['content']['Introduction'])
        output.append("")
    
    # Add categories
    if content['categories']:
        output.append("CATEGORIES:")
        for category in content['categories']:
            output.append(f"- {category}")
        output.append("")
    
    # Add source URL
    output.append(f"Source: {content['url']}")
    
    # Join all sections with newlines
    result = '\n'.join(output)
    
    # Final sanitization
    return sanitize_file_content(result, remove_html=True)


def process_wikipedia_urls(csv_file="artist_urls.csv", output_dir="blues_artist_data"):
    """
    Process all Wikipedia URLs from the CSV file
    
    Args:
        csv_file (str): Path to the CSV file with artist URLs
        output_dir (str): Directory to save the extracted content
    """
    try:
        # Load the CSV file
        df = pd.read_csv(csv_file)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Filter for rows with Wikipedia URLs
        wikipedia_artists = []
        for idx, row in df.iterrows():
            artist_name = row['name']
            url = row['url']
            
            if isinstance(url, str) and is_wikipedia_url(url):
                # Remove quotes from artist name
                clean_name = artist_name.replace('"', '')
                wikipedia_artists.append((clean_name, url))
        
        if not wikipedia_artists:
            print("No Wikipedia URLs found in the CSV file.")
            return
        
        print(f"Found {len(wikipedia_artists)} artists with Wikipedia URLs")
        
        # Process each Wikipedia artist
        for artist_name, url in wikipedia_artists:
            print(f"Processing Wikipedia page for {artist_name}")
            
            try:
                # Get Wikipedia content
                wikipedia_content = get_wikipedia_content(url)
                
                # Format the content
                formatted_content = format_wikipedia_content(wikipedia_content)
                
                # Create artist directory with sanitized name
                safe_artist_name = sanitize_filename(artist_name)
                artist_dir = os.path.join(output_dir, safe_artist_name)
                os.makedirs(artist_dir, exist_ok=True)
                
                # Save artist info with new filename pattern
                output_file = os.path.join(artist_dir, f"{safe_artist_name}_wikipedia.txt")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                
                print(f"  Saved Wikipedia information for {artist_name}")
                
            except Exception as e:
                print(f"  Error processing {artist_name}: {str(e)}")
            
            # Be nice to Wikipedia's servers
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    process_wikipedia_urls()