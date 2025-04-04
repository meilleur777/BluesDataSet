import os
import re
import string
import subprocess
import platform
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class BluesIRSystem:
    """Boolean Information Retrieval System for blues artist data."""
    
    def __init__(self, data_directory="blues_artist_data"):
        """Initialize the IR system with the data directory path."""
        self.data_directory = data_directory
        self.inverted_index = defaultdict(set)  # Maps terms to document IDs
        self.document_map = {}  # Maps document IDs to their file paths
        self.doc_id_counter = 0
        self.stop_words = set(stopwords.words('english'))
        
        # Additional music-specific stop words (removed 'blues')
        self.stop_words.update(['music', 'musician', 'artist', 'song', 'songs'])
        
    def open_file_with_default_application(self, file_path):
        """
        Open a file with the default application based on the operating system.
        
        Args:
            file_path: Path to the file to open
        """
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux and other Unix-like systems
                subprocess.call(['xdg-open', file_path])
            print(f"Opened file with default application: {file_path}")
            return True
        except Exception as e:
            print(f"Error opening file with default application: {e}")
            return False
    
    def open_document_by_id(self, doc_id):
        """
        Open a document by its ID using the default application.
        
        Args:
            doc_id: ID of the document to open (integer)
            
        Returns:
            Boolean indicating if document was found and opened
        """
        try:
            # Convert string to integer if needed
            if isinstance(doc_id, str):
                doc_id = int(doc_id)
                
            # Check if document ID exists
            if doc_id not in self.document_map:
                print(f"Document ID {doc_id} not found.")
                return False
            
            # Get file path and open with default application
            file_path = self.document_map[doc_id]['path']
            artist = self.document_map[doc_id]['artist']
            filename = self.document_map[doc_id]['filename']
            
            print(f"Opening document ID {doc_id}: {artist} - {filename}")
            return self.open_file_with_default_application(file_path)
            
        except ValueError:
            print(f"Invalid document ID format: {doc_id}. Please provide a valid integer ID.")
            return False
        except Exception as e:
            print(f"Error opening document ID {doc_id}: {e}")
            return False
    
    def preprocess_text(self, text):
        """
        Preprocess text by:
        1. Converting to lowercase
        2. Removing punctuation
        3. Tokenizing
        4. Removing stop words
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Remove single character tokens and digits
        tokens = [token for token in tokens if len(token) > 1 and not token.isdigit()]
        
        return tokens
    
    def build_index(self):
        """
        Build the inverted index from the blues artist data files.
        This scans all text files and creates an index mapping terms to documents.
        """
        print(f"Building index from {self.data_directory}...")
        
        # Reset indexes
        self.inverted_index = defaultdict(set)
        self.document_map = {}
        self.doc_id_counter = 0
        
        # Walk through the data directory
        for artist_dir in os.listdir(self.data_directory):
            artist_path = os.path.join(self.data_directory, artist_dir)
            
            # Skip if not a directory
            if not os.path.isdir(artist_path):
                continue
                
            # Process each text file in the artist directory
            for filename in os.listdir(artist_path):
                if not filename.endswith('.txt'):
                    continue
                
                file_path = os.path.join(artist_path, filename)
                doc_id = self.doc_id_counter
                self.doc_id_counter += 1
                
                # Map document ID to file path
                self.document_map[doc_id] = {
                    'path': file_path,
                    'artist': artist_dir,
                    'filename': filename
                }
                
                # Process file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        tokens = self.preprocess_text(content)
                        
                        # Add each token to the inverted index
                        for token in set(tokens):  # Using set to count each term only once per document
                            self.inverted_index[token].add(doc_id)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        print(f"Index built successfully: {len(self.inverted_index)} terms and {len(self.document_map)} documents.")
    
    def parse_boolean_query(self, query):
        """
        Parse a Boolean query into a structured format.
        
        Supports:
        - AND: term1 AND term2
        - OR: term1 OR term2
        - NOT: NOT term
        - Parentheses for grouping: (term1 AND term2) OR term3
        
        Returns a function that evaluates the query on a document.
        """
        # Preprocess the query
        query = query.upper()  # Convert operators to uppercase
        
        # Add spaces around parentheses for tokenization
        query = query.replace('(', ' ( ').replace(')', ' ) ')
        
        # Tokenize
        tokens = query.split()
        
        # Simple case: single term
        if len(tokens) == 1:
            term = tokens[0].lower()
            return self.inverted_index.get(term, set())
        
        # Parse the query recursively
        return self._evaluate_query(tokens)
    
    def _evaluate_query(self, tokens):
        """Evaluate a Boolean query recursively."""
        # Stack for operands
        operands = []
        # Stack for operators
        operators = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token == '(':
                # Find matching closing parenthesis
                j = i + 1
                depth = 1
                while j < len(tokens) and depth > 0:
                    if tokens[j] == '(':
                        depth += 1
                    elif tokens[j] == ')':
                        depth -= 1
                    j += 1
                
                # Evaluate subquery within parentheses
                result = self._evaluate_query(tokens[i+1:j-1])
                operands.append(result)
                i = j
            
            elif token == 'AND' or token == 'OR':
                operators.append(token)
                i += 1
            
            elif token == 'NOT':
                # Get the next token
                next_token = tokens[i+1].lower()
                
                if next_token == '(':
                    # Handle NOT with parentheses
                    j = i + 2
                    depth = 1
                    while j < len(tokens) and depth > 0:
                        if tokens[j] == '(':
                            depth += 1
                        elif tokens[j] == ')':
                            depth -= 1
                        j += 1
                    
                    # Get documents matching the subquery
                    result = self._evaluate_query(tokens[i+2:j-1])
                    # Apply NOT operation (all documents except those in result)
                    all_docs = set(self.document_map.keys())
                    operands.append(all_docs - result)
                    i = j
                else:
                    # Handle single-term NOT
                    term = tokens[i+1].lower()
                    term_docs = self.inverted_index.get(term, set())
                    all_docs = set(self.document_map.keys())
                    operands.append(all_docs - term_docs)
                    i += 2
            
            else:
                # Regular term
                term = token.lower()
                operands.append(self.inverted_index.get(term, set()))
                i += 1
        
        # Apply operators in order (no precedence for simplicity)
        result = operands[0] if operands else set()
        for i in range(len(operators)):
            if operators[i] == 'AND':
                result = result.intersection(operands[i+1])
            elif operators[i] == 'OR':
                result = result.union(operands[i+1])

        return result
    
    def search(self, query_string):
        """
        Search for documents matching the Boolean query.
        
        Args:
            query_string: A Boolean query string (e.g., "muddy AND waters NOT howlin")
            
        Returns:
            A list of matching document information
        """
        matching_docs = self.parse_boolean_query(query_string)
        
        results = []
        for doc_id in matching_docs:
            doc_info = self.document_map[doc_id]
            results.append({
                'id': doc_id,
                'artist': doc_info['artist'],
                'filename': doc_info['filename'],
                'path': doc_info['path']
            })
        
        return results
    
    def get_document_content(self, doc_id):
        """
        Get the content of a document by its ID.
        
        Args:
            doc_id: The ID of the document
            
        Returns:
            The content of the document
        """
        if doc_id not in self.document_map:
            return "Document not found"
        
        file_path = self.document_map[doc_id]['path']
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error reading document: {e}"
    
    def run_interactive(self):
        """
        Run an interactive search session.
        """
        print("\nBlues Artist IR System (Boolean Model)")
        print("=====================================")
        print("Enter Boolean queries with AND, OR, NOT operators")
        print("Example: muddy AND waters")
        print("Enter 'q' to quit")
        print("Enter 'stats' to see index statistics")
        print("Enter 'help' to see example queries")
        print("Enter 'open <id>' to open a document directly by ID")
        print("=====================================\n")
        
        while True:
            query = input("\nEnter your query: ")
            
            if query.lower() == 'q':
                break
            
            if query.lower() == 'stats':
                print(f"Index contains {len(self.inverted_index)} terms")
                print(f"Index contains {len(self.document_map)} documents")
                print(f"Top 10 terms by document frequency:")
                sorted_terms = sorted(self.inverted_index.items(), key=lambda x: len(x[1]), reverse=True)
                for i, (term, docs) in enumerate(sorted_terms[:10]):
                    print(f"  {i+1}. '{term}' appears in {len(docs)} documents")
                continue
            
            if query.lower() == 'help':
                print("Example queries:")
                print("  muddy AND waters")
                print("  king NOT bb")
                print("  guitar OR harmonica")
                print("  chicago AND (guitar OR harmonica)")
                print("  (muddy AND waters) OR (howlin AND wolf)")
                print("  open 5 - Opens document with ID 5 in your default text viewer")
                continue
            
            # Handle 'open <id>' command
            if query.lower().startswith('open '):
                doc_id_str = query[5:].strip()
                try:
                    self.open_document_by_id(doc_id_str)
                except ValueError:
                    print(f"Invalid document ID: {doc_id_str}")
                continue
            
            results = self.search(query)
            
            if not results:
                print("No matching documents found.")
                continue
            
            print(f"\nFound {len(results)} matching documents:")
            print(f"{'#':<4} {'Doc ID':<8} {'Artist':<25} {'Filename':<30}")
            print("-" * 70)
            for i, result in enumerate(results):
                print(f"{i+1:<4} {result['id']:<8} {result['artist']:<25} {result['filename']:<30}")
            
            print("\nNote: Document IDs are used for relevance judgments in evaluation")
            
            while True:
                view = input("\nEnter number to view document content, 'o#' to open with default app, 'id#' to open by ID, or 'b' to go back: ")
                if view.lower() == 'b':
                    break
                
                # Handle open with default application command
                if view.lower().startswith('o') and view[1:].isdigit():
                    try:
                        open_idx = int(view[1:]) - 1
                        if 0 <= open_idx < len(results):
                            doc_id = results[open_idx]['id']
                            file_path = self.document_map[doc_id]['path']
                            self.open_file_with_default_application(file_path)
                        else:
                            print("Invalid document number.")
                    except ValueError:
                        print("Please enter a valid format (o1, o2, etc.).")
                    continue
                
                # Handle open by document ID command
                if view.lower().startswith('id') and view[2:].isdigit():
                    try:
                        doc_id = int(view[2:])
                        self.open_document_by_id(doc_id)
                    except ValueError:
                        print("Please enter a valid format (id1, id2, etc.).")
                    continue
                
                # Handle standard view in terminal
                try:
                    view_index = int(view) - 1
                    if 0 <= view_index < len(results):
                        doc_id = results[view_index]['id']
                        content = self.get_document_content(doc_id)
                        file_path = self.document_map[doc_id]['path']
                        
                        # Display the document content with some formatting
                        print("\n" + "=" * 80)
                        print(f"Document ID: {doc_id}")
                        print(f"Document: {results[view_index]['filename']}")
                        print(f"Artist: {results[view_index]['artist']}")
                        print(f"Path: {file_path}")
                        print("=" * 80)
                        
                        # Print a preview (first 500 characters)
                        preview_length = 500
                        if len(content) > preview_length:
                            print(content[:preview_length] + "...")
                            more = input("Display more (y), open with default application (o), or continue (n)? ")
                            if more.lower() == 'y':
                                print("\n" + content)
                            elif more.lower() == 'o':
                                self.open_file_with_default_application(file_path)
                        else:
                            print(content)
                            open_option = input("Open with default application (y/n)? ")
                            if open_option.lower() == 'y':
                                self.open_file_with_default_application(file_path)
                    else:
                        print("Invalid document number.")
                except ValueError:
                    print("Please enter a valid number or command.")

if __name__ == "__main__":
    # Initialize the IR system
    ir_system = BluesIRSystem()
    
    # Build the index
    ir_system.build_index()
    
    # Run interactive search
    ir_system.run_interactive()
