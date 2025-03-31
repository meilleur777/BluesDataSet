#!/usr/bin/env python
"""
Blues Brothers Query Evaluator

This script evaluates the IR system for the query "blues AND brothers" and appends
the evaluation results to the test_queries.json file with relevance judgments based on specific criteria:
1. Documents returned by the IR system for "blues AND brothers"
2. Documents containing the exact phrase "blues brothers"
3. Documents containing the exact phrase "the blues brothers"

Documents meeting criteria 2 or 3 are considered truly relevant.
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
    Generate test query for "blues AND brothers" and append it to test_queries.json.
    """
    # Initialize the IR system
    print("Initializing IR system...")
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(parent_dir, "blues_artist_data")
    ir_system = BluesIRSystem(data_directory=data_dir)
    ir_system.build_index()
    
    # Run the Boolean query
    query = "blues AND brothers"
    print(f"Running query: '{query}'")
    boolean_results = ir_system.search(query)
    boolean_doc_ids = {result['id'] for result in boolean_results}
    
    # Search for exact phrases
    data_directory = ir_system.data_directory
    print("Searching for phrase 'blues brothers'...")
    phrase1_doc_ids = search_phrase_in_files(data_directory, "blues brothers")
    
    print("Searching for phrase 'the blues brothers'...")
    phrase2_doc_ids = search_phrase_in_files(data_directory, "the blues brothers")
    
    # Combine relevant document IDs (those containing either phrase)
    relevant_doc_ids = phrase1_doc_ids.union(phrase2_doc_ids)
    
    # Create comments for each document
    comments = {}
    for doc_id in boolean_doc_ids:
        if doc_id in phrase1_doc_ids and doc_id in phrase2_doc_ids:
            comments[str(doc_id)] = "Contains both 'blues brothers' and 'the blues brothers' phrases"
        elif doc_id in phrase1_doc_ids:
            comments[str(doc_id)] = "Contains 'blues brothers' phrase"
        elif doc_id in phrase2_doc_ids:
            comments[str(doc_id)] = "Contains 'the blues brothers' phrase"
        else:
            comments[str(doc_id)] = "Retrieved by Boolean query but does not contain target phrases"
    
    # Identify false negatives (relevant docs not retrieved by Boolean query)
    for doc_id in relevant_doc_ids:
        if doc_id not in boolean_doc_ids:
            doc_info = ir_system.document_map.get(doc_id, {})
            artist = doc_info.get('artist', 'Unknown')
            filename = doc_info.get('filename', 'Unknown')
            
            comment = "Relevant but not retrieved by Boolean query. "
            if doc_id in phrase1_doc_ids and doc_id in phrase2_doc_ids:
                comment += "Contains both 'blues brothers' and 'the blues brothers' phrases"
            elif doc_id in phrase1_doc_ids:
                comment += "Contains 'blues brothers' phrase"
            else:
                comment += "Contains 'the blues brothers' phrase"
            
            comments[str(doc_id)] = comment
    
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
    print(f"Documents with 'blues brothers': {len(phrase1_doc_ids)}")
    print(f"Documents with 'the blues brothers': {len(phrase2_doc_ids)}")
    print(f"True relevant documents: {len(relevant_doc_ids)}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Create the query object
    new_query = {
        "id": "Q1",
        "query": "blues AND brothers",
        "description": "Documents about The Blues Brothers",
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
