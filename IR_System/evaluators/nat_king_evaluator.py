#!/usr/bin/env python
"""
Nat King Cole Query Evaluator

This script evaluates the IR system for the query "nat AND king" and appends
the evaluation results to test_queries.json with relevance judgments based on specific criteria:
1. Documents returned by the IR system for "nat AND king"
2. Documents containing the exact phrase "nat king cole"

Documents meeting criterion 2 are considered truly relevant.
"""

import os
import json
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blues_ir_system import BluesIRSystem

def search_phrase_in_files(data_directory, phrase):
    """
    Search for an exact phrase in all text files in the data directory.
    
    Args:
        data_directory: Directory containing artist subdirectories with text files
        phrase: The exact phrase to search for
        
    Returns:
        Set of document IDs where the phrase was found
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
    
    # Now search for the phrase in all files
    phrase_lower = phrase.lower()
    for file_path, doc_id in doc_id_map.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().lower()
                if phrase_lower in content:
                    results.add(doc_id)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return results

def append_test_query():
    """
    Generate test query for "nat AND king" and append it to test_queries.json.
    """
    # Initialize the IR system
    print("Initializing IR system...")
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(parent_dir, "blues_artist_data")
    ir_system = BluesIRSystem(data_directory=data_dir)
    ir_system.build_index()
    
    # Run the Boolean query
    query = "nat AND king"
    print(f"Running query: '{query}'")
    boolean_results = ir_system.search(query)
    boolean_doc_ids = {result['id'] for result in boolean_results}
    
    # Search for exact phrase
    data_directory = ir_system.data_directory
    print("Searching for phrase 'nat king cole'...")
    relevant_doc_ids = search_phrase_in_files(data_directory, "nat king cole")
    
    # Create comments for each document
    comments = {}
    for doc_id in boolean_doc_ids:
        if doc_id in relevant_doc_ids:
            comments[str(doc_id)] = "Contains 'nat king cole' phrase - relevant"
        else:
            comments[str(doc_id)] = "Retrieved by Boolean query but does not contain 'nat king cole' phrase - not relevant"
    
    # Identify false negatives (relevant docs not retrieved by Boolean query)
    for doc_id in relevant_doc_ids:
        if doc_id not in boolean_doc_ids:
            doc_info = ir_system.document_map.get(doc_id, {})
            artist = doc_info.get('artist', 'Unknown')
            filename = doc_info.get('filename', 'Unknown')
            comments[str(doc_id)] = "Contains 'nat king cole' phrase but not retrieved by Boolean query - relevant but missed"
    
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
    print(f"Documents with 'nat king cole': {len(relevant_doc_ids)}")
    print(f"True relevant documents: {len(relevant_doc_ids)}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Create the query object
    new_query = {
        "id": "Q2",
        "query": "nat AND king",
        "description": "Documents about Nat King Cole",
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
