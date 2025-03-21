# Blues Artist Information Retrieval System

A Boolean Information Retrieval (IR) system for searching through blues artist text data. This system allows you to perform complex searches with Boolean operators (AND, OR, NOT) to find relevant information about blues musicians.

## Features

- **Boolean Search**: Full support for AND, OR, NOT operators and parentheses grouping
- **Text Preprocessing**: Automatic handling of lowercase conversion, punctuation removal, and stopword filtering
- **Interactive Interface**: User-friendly command-line interface for exploring the data
- **Document Preview**: View matching document content directly in the terminal
- **Index Statistics**: See which terms appear most frequently across the document collection

## Requirements

- Python 3.6+
- NLTK (Natural Language Toolkit)
- A collection of text files in the `blues_artist_data` directory

## Installation

1. Clone this repository or download the files:
   ```
   git clone https://github.com/yourusername/blues-ir-system.git
   cd blues-ir-system
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Make sure you have the `blues_artist_data` directory (output from the Text_Collector component) in the correct location. Current repository has sample output from Text_Collector.

## Usage

1. Run the IR system:
   ```
   python blues_ir_system.py
   ```

2. The system will build an index of all the terms in your documents.

3. Once the index is built, you can enter Boolean queries at the prompt. For example:
   ```
   Enter your query: muddy AND waters
   ```

4. View the list of results and select a document number to see its content.

5. Special commands:
   - Type `help` to see example queries
   - Type `stats` to see index statistics
   - Type `q` to quit the program

## Example Queries

- `muddy AND waters` - Find documents mentioning both "muddy" and "waters"
- `chicago AND (guitar OR harmonica)` - Find documents mentioning "chicago" and either "guitar" or "harmonica"
- `king NOT bb` - Find documents mentioning "king" but not "bb"
- `(muddy AND waters) OR (howlin AND wolf)` - Complex query with grouped terms

## How It Works

This system uses the Boolean retrieval model for information retrieval:

1. **Indexing Phase**:
   - Scans all text files in the `blues_artist_data` directory
   - Processes each document (tokenization, normalization, stopword removal)
   - Builds an inverted index mapping terms to document IDs

2. **Search Phase**:
   - Parses Boolean queries into their components
   - Retrieves document sets for each term
   - Applies Boolean operations (AND, OR, NOT) to these sets
   - Returns matching documents in an easily readable format

Example of the inverted index structure:
```
{
  "muddy": {0, 2},     # "muddy" appears in documents 0 and 2
  "waters": {0, 2},    # "waters" appears in documents 0 and 2 
  "guitar": {0, 1},    # "guitar" appears in documents 0 and 1
  "chicago": {0, 2},   # etc.
  ...
}
```

## Limitations

- **No Ranking**: All matching documents are considered equally relevant
- **Binary Logic**: Terms are either present or absent, with no partial matching
- **No Fuzzy Matching**: Misspellings and variant spellings aren't handled
- **Simple Model**: Doesn't use advanced IR techniques like TF-IDF weighting or semantic understanding

## Future Extensions

Potential improvements for future versions:

- Add support for phrase queries (e.g., "Muddy Waters" as an exact phrase)
- Implement wildcard searches (e.g., "blue*" to match "blues", "bluesy", etc.)
- Add spelling correction for query terms
- Extend to a Vector Space Model for ranked retrieval
