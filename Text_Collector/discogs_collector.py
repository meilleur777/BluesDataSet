import os
import re
import pandas as pd
import requests
import time
from urllib.parse import urlparse
from discogs_oauth_client import DiscogsOAuthClient

def extract_discogs_id_from_url(url):
    """
    Extract the artist ID from a Discogs URL
    Example URL format: https://www.discogs.com/artist/683547-JT-Brown
    """
    pattern = r'/artist/(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def collect_artist_info_from_discogs(artist_name, artist_id):
    """
    Collect information about an artist from Discogs using the API
    """
    # Initialize OAuth client
    client = DiscogsOAuthClient()
    
    # Check if we already have tokens in the environment
    access_token = os.getenv("DISCOGS_OAUTH_TOKEN")
    access_token_secret = os.getenv("DISCOGS_OAUTH_TOKEN_SECRET")
    
    if not access_token or not access_token_secret:
        # Complete OAuth flow if no tokens are saved
        auth_result = client.complete_oauth_flow()
        access_token = auth_result["oauth_token"]
        access_token_secret = auth_result["oauth_token_secret"]
    else:
        # Set tokens from environment
        client.access_token = access_token
        client.access_token_secret = access_token_secret
    
    # Generate required OAuth parameters
    oauth_timestamp = str(int(time.time()))
    oauth_nonce = client.generate_nonce()
    
    # Create Authorization header
    auth_header = (
        'OAuth oauth_consumer_key="' + client.consumer_key + '",'
        'oauth_nonce="' + oauth_nonce + '", '
        'oauth_token="' + client.access_token + '", '
        'oauth_signature="' + client.consumer_secret + '&' + client.access_token_secret + '", '
        'oauth_signature_method="PLAINTEXT", '
        'oauth_timestamp="' + oauth_timestamp + '"'
    )
    
    # Set up headers
    headers = {
        'Authorization': auth_header,
        'User-Agent': client.user_agent
    }
    
    # Artist endpoint
    artist_url = f"{client.api_url}/artists/{artist_id}"
    
    print(f"Requesting data for artist {artist_name} (ID: {artist_id}) from Discogs API...")
    
    # Make the request
    response = requests.get(artist_url, headers=headers)
    
    # Check for success
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"Failed to get artist data: {response.text}")
    
    # Parse the response
    artist_data = response.json()
    
    # Extract relevant information
    profile = artist_data.get("profile", "")
    
    # Extract information about influences
    # Profile text often contains info about who influenced the artist
    influence_info = {
        "name": artist_name,
        "profile": profile,
        "urls": artist_data.get("urls", []),
        "discogs_id": artist_id
    }
    
    return influence_info

def sanitize_filename(name):
    """
    Sanitize a string to be used as a filename or directory name.
    Removes or replaces invalid characters.
    """
    # Replace problematic characters with underscores
    invalid_chars = r'[<>:"/\\|?*\']'
    sanitized = re.sub(invalid_chars, '_', name)
    
    # Replace multiple consecutive underscores with a single one
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Trim any trailing spaces or dots (problematic on Windows)
    sanitized = sanitized.strip('. ')
    
    return sanitized

def process_discogs_urls(csv_file="artist_urls.csv", output_dir="artist_data"):
    """
    Process all Discogs URLs from the CSV file using the Discogs API
    """
    try:
        # Load the CSV file
        df = pd.read_csv(csv_file)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Filter for rows with Discogs URLs
        discogs_artists = []
        for idx, row in df.iterrows():
            artist_name = row['name']
            url = row['url']
            
            if "discogs.com" in str(url):
                # Remove quotes from artist name
                clean_name = artist_name.replace('"', '')
                discogs_artists.append((clean_name, url))
        
        if not discogs_artists:
            print("No Discogs URLs found in the CSV file.")
            return
        
        print(f"Found {len(discogs_artists)} artists with Discogs URLs")
        
        # Process each Discogs artist
        for artist_name, url in discogs_artists:
            print(f"Processing Discogs URL for {artist_name}")
            
            # Extract Discogs ID
            artist_id = extract_discogs_id_from_url(url)
            
            if not artist_id:
                print(f"  Could not extract Discogs ID from URL: {url}")
                continue
            
            try:
                # Collect artist info
                artist_info = collect_artist_info_from_discogs(artist_name, artist_id)
                
                # Create artist directory with sanitized name
                safe_artist_name = sanitize_filename(artist_name)
                artist_dir = os.path.join(output_dir, safe_artist_name.replace(" ", "_"))
                os.makedirs(artist_dir, exist_ok=True)
                
                # Save artist info
                output_file = os.path.join(artist_dir, f"{safe_artist_name.replace(' ', '_')}_influence.txt")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"ARTIST: {artist_name}\n\n")
                    f.write(f"PROFILE:\n{artist_info['profile']}\n\n")
                    f.write("RELATED URLS:\n")
                    for related_url in artist_info['urls']:
                        f.write(f"- {related_url}\n")
                    f.write(f"\nSource: https://www.discogs.com/artist/{artist_id}")
                
                print(f"  Saved Discogs information for {artist_name}")
                
            except Exception as e:
                print(f"  Error processing {artist_name}: {str(e)}")
            
            # Sleep to avoid rate limits
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    process_discogs_urls()