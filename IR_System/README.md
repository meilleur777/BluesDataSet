# Blues Artist Information Retrieval System

A Boolean Information Retrieval system for searching through blues artist text data. This system allows you to perform simple searches with Boolean operators (AND, OR, NOT) to find relevant information about blues musicians.

## Features

- **Boolean Search**: Full support for AND, OR, NOT operators and parentheses grouping
- **Text Preprocessing**: Automatic handling of lowercase conversion, punctuation removal, and stopword filtering
- **Interactive Interface**: User-friendly command-line interface for exploring the data
- **Document Preview**: View matching document content directly in the terminal
- **External Viewer**: Open documents in your default text editor by ID

## Installation

1. Clone this repository or download the files:
   ```
   git clone https://github.com/meilleur777/BluesDataSet.git
   cd BluesDataSet/IR_System
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Install required NLTK resources:
   ```
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```
   This step is essential as the system requires these NLTK resources for text processing.

4. Make sure you have the `blues_artist_data` directory with text files about blues artists.

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
   - Type `open <id>` to open a document with the specified ID in your default text viewer
   - Type `q` to quit the program

## Specialized Evaluators

The system includes specialized evaluators for specific queries:

1. **Blues Brothers Evaluator**: Evaluates the query "blues AND brothers" against documents containing "blues brothers" or "the blues brothers"
   ```
   python blues_brothers_evaluator.py
   ```

2. **Nat King Evaluator**: Evaluates the query "nat AND king" against documents containing "nat king cole"
   ```
   python nat_king_evaluator.py
   ```

3. **Three Kings Evaluator**: Evaluates a query for documents containing all three blues kings (B.B. King, Albert King, and Freddie King)
   ```
   python three_kings_evaluator.py
   ```

These evaluators append their results to a `test_queries.json` file that can be used for query testing.

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