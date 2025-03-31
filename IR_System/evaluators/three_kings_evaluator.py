#!/usr/bin/env python
"""
Three Kings Query Evaluator

This script evaluates the IR system for the query "(bb AND king) AND (albert AND king) AND (Freddie AND king)"
and appends the evaluation results to test_queries.json with relevance judgments based on specific criteria:
1. Documents returned by the IR system for the complex Boolean query
2. Documents containing all three blues kings: "b.b. king", "albert king", and "freddie king"

Documents meeting criterion 2 are considered truly relevant.
"""

import os
import json
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blues_ir_system import BluesIRSystem

def search_multiple_phrases_in_files(data_directory, phrases):
    """
    Search for multiple exact phrases in all text files in the data directory.
    Only documents containing ALL phrases are returned.
    
    Args:
        data_directory: Directory containing artist subdirectories with text files
        phrases: List of exact phrases to search for
        
    Returns:
        Set of document IDs where ALL phrases were found
    """
    results = set()
    doc_id_map = {}
    doc_id = 0
    
    # First, build a mapping of file paths to document IDs
    for artist_dir in os.listdir(data_directory):
        artist_path = os.path.join(data_directory, artist_dir)
        
        # Skip if not a directory
        if not os.path.isdir(artist_path):
            continue
            
        # Process each text file in the artist directory
        for filename in os.listdir(artist_path):
            if not filename.endswith('.txt'):
                continue
            
            file_path = os.path.join(artist_path, filename)
            doc_id_map[file_path] = doc_id
            doc_id += 1
    
    # Initialize results with all document IDs
    all_docs = set(doc_id_map.values())
    
    # Track individual phrase matches for comments
    phrase_matches = {phrase: set() for phrase in phrases}
    
    # Search for each phrase in all files
    for file_path, doc_id in doc_id_map.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().lower()
                
                # Check each phrase
                for phrase in phrases:
                    phrase_lower = phrase.lower()
                    if phrase_lower in content:
                        phrase_matches[phrase].add(doc_id)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Find documents containing ALL phrases
    results = all_docs
    for phrase, matches in phrase_matches.items():
        results = results.intersection(matches)
    
    return results, phrase_matches

def append_test_query():
    """
    Generate test query for Three Kings and append it to test_queries.json.
    """
    # Initialize the IR system
    print("Initializing IR system...")
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(parent_dir, "blues_artist_data")
    ir_system = BluesIRSystem(data_directory=data_dir)
    ir_system.build_index()
    
    # Run the Boolean query
    query = "(bb AND king) AND (albert AND king) AND (freddie AND king)"
    print(f"Running query: '{query}'")
    boolean_results = ir_system.search(query)
    boolean_doc_ids = {result['id'] for result in boolean_results}
    
    # Search for all three kings
    data_directory = ir_system.data_directory
    king_phrases = ["b.b. king", "albert king", "freddie king"]
    print(f"Searching for all three kings: {', '.join(king_phrases)}...")
    relevant_doc_ids, phrase_matches = search_multiple_phrases_in_files(data_directory, king_phrases)
    
    # Create comments for each document
    comments = {}
    
    # Comment on boolean query results
    for doc_id in boolean_doc_ids:
        # Determine which kings are mentioned in this document
        kings_mentioned = []
        for phrase, matches in phrase_matches.items():
            if doc_id in matches:
                kings_mentioned.append(phrase)
        
        if doc_id in relevant_doc_ids:
            comments[str(doc_id)] = "Contains references to all three Kings (B.B., Albert, and Freddie) - relevant"
        else:
            kings_str = ", ".join(kings_mentioned) if kings_mentioned else "none"
            comments[str(doc_id)] = f"Retrieved by Boolean query but does not mention all three Kings. Kings mentioned: {kings_str} - not relevant"
    
    # Identify false negatives (relevant docs not retrieved by Boolean query)
    for doc_id in relevant_doc_ids:
        if doc_id not in boolean_doc_ids:
            doc_info = ir_system.document_map.get(doc_id, {})
            artist = doc_info.get('artist', 'Unknown')
            filename = doc_info.get('filename', 'Unknown')
            comments[str(doc_id)] = "Contains all three Kings (B.B., Albert, and Freddie) but not retrieved by Boolean query - relevant but missed"
    
    # Calculate precision and recall
    true_positives = len(boolean_doc_ids.intersection(relevant_doc_ids))
    retrieved = len(boolean_doc_ids)
    relevant = len(relevant_doc_ids)
    
    precision = true_positives / retrieved if retrieved > 0 else 0
    recall = true_positives / relevant if relevant > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0
    
    # Print evaluation summary
    print("\n====== Evaluation Summary ======")
    print(f"Boolean query results: {len(boolean_doc_ids)} documents")
    print(f"Documents with all three Kings: {len(relevant_doc_ids)}")
    print(f"True relevant documents: {len(relevant_doc_ids)}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Create the query object
    new_query = {
        "id": "Q3",
        "query": "(bb AND king) AND (albert AND king) AND (freddie AND king)",
        "description": "Documents mentioning all three Kings of Blues (B.B., Albert, and Freddie)",
        "relevant_docs": list(relevant_doc_ids),
        "comments": comments
    }
    
    # Read existing queries or create new list
    output_file = "test_queries.json"
    queries = []
    
    try:
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                queries = json.load(f)
                
            # Check if this query ID already exists
            for i, q in enumerate(queries):
                if q.get('id') == new_query['id']:
                    print(f"Replacing existing query with ID {new_query['id']}")
                    queries[i] = new_query
                    break
            else:
                # If we didn't break the loop, add the new query
                queries.append(new_query)
        else:
            queries = [new_query]
            
        # Write updated queries back to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(queries, f, indent=2)
        
        print(f"\nQuery appended to {output_file}")
        print(f"Query has {len(relevant_doc_ids)} relevant documents with comments")
        
    except Exception as e:
        print(f"Error updating test_queries.json: {e}")
    
    return new_query

if __name__ == "__main__":
    append_test_query()
