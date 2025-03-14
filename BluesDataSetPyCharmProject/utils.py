# utils.py - Utility functions
import os

def save_to_txt(data, filename):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        with open(filename, "w", encoding="utf-8") as f:
            for item in data:
                f.write(item + "\n")
        print(f"Data saved to {filename}")
    except OSError as e:
        print(f"Error writing to file {filename}: {e}")
