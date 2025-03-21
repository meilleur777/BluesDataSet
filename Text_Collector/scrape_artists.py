import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse
from sanitizer import sanitize_text, sanitize_filename, sanitize_file_content

def load_artist_urls(csv_file="artist_urls.csv"):
    """Load the consolidated artist URLs from CSV."""
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        print(f"Error loading {csv_file}: {str(e)}")
        return None

def create_output_directory(base_dir="blues_artist_data"):
    """Create the output directory for scraped content."""
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def is_relevant_content(text, categories):
    """Check if the text contains any of the relevant categories."""
    text_lower = text.lower()
    return any(category.lower() in text_lower for category in categories)

def get_influence_content(soup, categories):
    """
    Extract paragraphs containing information about influences.
    
    This function looks for paragraphs that:
    1. Contain category keywords (biography, life, career, style)
    2. Contain influence-related keywords
    """
    influence_keywords = [
        "influence", "influenced", "inspiration", "inspired", 
        "mentor", "teacher", "student", "follow", "admire",
        "style", "technique", "approach", "method", "sound",
        "impact", "legacy", "contribution", "innovate", "pioneer"
    ]
    
    relevant_paragraphs = []
    
    # Find all paragraphs
    paragraphs = soup.find_all('p')
    
    for p in paragraphs:
        text = p.get_text(strip=True)
        
        # Check if paragraph contains any influence keywords
        has_influence = any(keyword in text.lower() for keyword in influence_keywords)
        
        # Check if paragraph relates to any of our categories
        is_relevant = is_relevant_content(text, categories)
        
        if has_influence and is_relevant and len(text) > 100:  # Minimum length to avoid fragments
            # Clean the text before adding
            clean_text = sanitize_text(text)
            relevant_paragraphs.append(clean_text)
    
    return relevant_paragraphs

def scrape_artist_content(artist_name, urls, categories, output_dir):
    """Scrape content about an artist from the provided URLs."""
    valid_urls = []
    
    # Validate URLs
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            valid_urls.append(url)
    
    if not valid_urls:
        print(f"No valid URLs found for {artist_name}")
        return False
    
    # Create artist directory with sanitized name
    safe_artist_name = sanitize_filename(artist_name)
    artist_dir = os.path.join(output_dir, safe_artist_name)
    os.makedirs(artist_dir, exist_ok=True)
    
    all_content = []
    
    # List of user agents to rotate
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    
    for url in valid_urls:
        # Skip discogs.com URLs as they'll be handled separately by discogs_collector.py
        if "discogs.com" in url:
            print(f"Skipping {url} - Discogs URLs are processed separately")
            continue
            
        # Skip wikipedia.org URLs as they'll be handled separately by wikipedia_collector.py
        if "wikipedia.org" in url:
            print(f"Skipping {url} - Wikipedia URLs are processed separately")
            continue
            
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"Scraping {url} (attempt {attempt+1}/{max_retries})")
                
                # Rotate user agents
                user_agent = user_agents[attempt % len(user_agents)]
                
                # Add headers to mimic a browser request
                headers = {
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://www.google.com/",
                    "DNT": "1",
                }
                
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get influence content
                influence_paragraphs = get_influence_content(soup, categories)
                
                if influence_paragraphs:
                    all_content.extend(influence_paragraphs)
                    
                    # Save URL source (clean it first)
                    all_content.append(f"\nSource: {sanitize_text(url)}\n")
                
                # Success - break the retry loop
                break
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"Access forbidden for {url} - site may be blocking scrapers")
                    break  # Don't retry on 403 errors
                else:
                    print(f"HTTP error on {url}: {str(e)}")
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
            
            # Only sleep and retry if this wasn't the last attempt
            if attempt < max_retries - 1:
                sleep_time = retry_delay * (attempt + 1)  # Increasing delay
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
    
    if all_content:
        # Save the scraped content with sanitized filename and new naming pattern
        output_file = os.path.join(artist_dir, f"{safe_artist_name}_web.txt")
        
        # Join content with double newlines
        file_content = "\n\n".join(all_content)
        
        # Final sanitization of the entire content
        file_content = sanitize_file_content(file_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"Saved influence information for {artist_name}")
        return True
    else:
        print(f"No relevant influence information found for {artist_name}")
        return False

def main():
    # Categories to look for
    categories = [
        "biography", "life", "career", "style", "history", 
        "music", "influence", "legacy", "impact", "development",
        "technique", "genre", "contribution", "background"
    ]
    
    # Load artist data
    artist_df = load_artist_urls()
    
    if artist_df is None:
        return
    
    print(f"Loaded {len(artist_df)} artists")
    
    # Create output directory
    output_dir = create_output_directory("blues_artist_data")
    
    # Track successful and failed scrapes
    success_count = 0
    
    # Process each artist
    for idx, row in artist_df.iterrows():
        artist_name = row['name']
        url = row['url']
        
        # Handle multiple URLs (if URL column contains multiple links)
        urls = [url.strip() for url in str(url).split(',')]
        
        print(f"Processing {artist_name} ({idx+1}/{len(artist_df)})")
        
        success = scrape_artist_content(artist_name, urls, categories, output_dir)
        if success:
            success_count += 1
    
    print(f"Completed scraping. Successfully gathered information for {success_count}/{len(artist_df)} artists")

if __name__ == "__main__":
    main()