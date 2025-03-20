import os
import glob
import pandas as pd
import re

def find_artist_csv_files(data_dir="blues_data"):
    """Find all CSV files containing 'artist' or 'musician' in their names."""
    pattern = os.path.join(data_dir, "*artist*.csv")
    artist_files = glob.glob(pattern)
    
    pattern = os.path.join(data_dir, "*musician*.csv")
    musician_files = glob.glob(pattern)
    
    return artist_files + musician_files

def process_csv_files(csv_files):
    """Extract artist names and URLs from CSV files and consolidate them."""
    all_artists = []
    
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            
            # Attempt to identify name and URL columns
            name_col = None
            url_col = None
            
            for col in df.columns:
                if re.search(r'name|artist|musician', col.lower()):
                    name_col = col
                elif re.search(r'url|link|website', col.lower()):
                    url_col = col
            
            if name_col and url_col:
                # Extract only the needed columns
                artist_data = df[[name_col, url_col]].copy()
                artist_data.columns = ['name', 'url']
                all_artists.append(artist_data)
            else:
                print(f"Could not identify name and URL columns in {file}")
        
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
    
    if all_artists:
        # Combine all dataframes
        combined_df = pd.concat(all_artists, ignore_index=True)
        
        # Remove duplicates based on name and URL
        unique_df = combined_df.drop_duplicates()
        
        return unique_df
    
    return None

def save_consolidated_csv(df, output_file="artist_urls.csv"):
    """Save the consolidated dataframe to a CSV file."""
    df.to_csv(output_file, index=False)
    print(f"Saved consolidated data to {output_file}")

def main():
    # Find relevant CSV files
    csv_files = find_artist_csv_files()
    
    if not csv_files:
        print("No matching CSV files found in blues_data directory")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    # Process the CSV files
    artist_df = process_csv_files(csv_files)
    
    if artist_df is not None and not artist_df.empty:
        print(f"Extracted information for {len(artist_df)} artists")
        save_consolidated_csv(artist_df)
    else:
        print("No artist information extracted")

if __name__ == "__main__":
    main()