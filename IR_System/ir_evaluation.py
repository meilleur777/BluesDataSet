import os
import json
from collections import defaultdict
from blues_ir_system import BluesIRSystem

class IRSystemEvaluator:
    """
    Evaluator for Boolean Information Retrieval Systems.
    Focuses on precision and recall metrics.
    """

    def __init__(self, ir_system):
        """Initialize the evaluator with an IR system."""
        self.ir_system = ir_system
        self.test_queries = []
        self.relevance_judgments = defaultdict(set)
        self.results_dir = "evaluation_results"

        # Create results directory if it doesn't exist
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def add_test_query(self, query_id, query_string, relevant_doc_ids, comments=None):
        """
        Add a test query with its relevant documents.

        Args:
            query_id: Unique identifier for the query
            query_string: The Boolean query string
            relevant_doc_ids: Set of document IDs that are relevant for this query
            comments: Optional dictionary mapping document IDs to relevance judgment comments
        """
        self.test_queries.append({
            'id': query_id,
            'query': query_string,
            'comments': comments or {}
        })
        self.relevance_judgments[query_id] = set(relevant_doc_ids)

    def load_test_queries_from_file(self, file_path):
        """
        Load test queries from a JSON file.

        The JSON file should have the format:
        [
            {
                "id": "Q1",
                "query": "muddy AND waters",
                "relevant_docs": [0, 2, 5],
                "comments": {
                    "0": "Directly about Muddy Waters' career",
                    "2": "Mentions Muddy Waters in context of Chicago blues",
                    "5": "Contains interview quotes from Muddy Waters"
                }
            },
            ...
        ]
        """
        try:
            with open(file_path, 'r') as f:
                queries_data = json.load(f)

            for query_data in queries_data:
                self.add_test_query(
                    query_data['id'],
                    query_data['query'],
                    set(query_data['relevant_docs']),
                    query_data.get('comments', {})
                )

            print(f"Loaded {len(queries_data)} test queries from {file_path}")
        except Exception as e:
            print(f"Error loading test queries: {e}")

    def save_relevance_judgments(self, file_path):
        """Save relevance judgments to a JSON file for future use."""
        data = {}
        for query_id, doc_ids in self.relevance_judgments.items():
            data[query_id] = list(doc_ids)

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved relevance judgments to {file_path}")

    def calculate_precision_recall(self, retrieved_docs, relevant_docs):
        """
        Calculate precision and recall for a single query.

        Args:
            retrieved_docs: Set of document IDs retrieved by the system
            relevant_docs: Set of document IDs that are relevant

        Returns:
            Dictionary with precision, recall, and F1 score
        """
        # Handle edge cases
        if not retrieved_docs and not relevant_docs:
            return {'precision': 1.0, 'recall': 1.0, 'f1': 1.0}

        if not retrieved_docs:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}

        if not relevant_docs:
            return {'precision': 0.0, 'recall': 1.0, 'f1': 0.0}

        # Calculate relevant documents that were retrieved
        relevant_retrieved = retrieved_docs.intersection(relevant_docs)
        num_relevant_retrieved = len(relevant_retrieved)

        # Calculate precision and recall
        precision = num_relevant_retrieved / len(retrieved_docs)
        recall = num_relevant_retrieved / len(relevant_docs)

        # Calculate F1 score
        f1 = 0.0
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)

        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'relevant_retrieved': num_relevant_retrieved,
            'retrieved': len(retrieved_docs),
            'relevant': len(relevant_docs)
        }

    def evaluate_all_queries(self):
        """
        Evaluate all test queries and return summary statistics.

        Returns:
            Dictionary with evaluation results for each query and overall averages
        """
        results = {}
        sum_precision = 0.0
        sum_recall = 0.0
        sum_f1 = 0.0

        for query in self.test_queries:
            query_id = query['id']
            query_string = query['query']
            comments = query.get('comments', {})

            # Get relevant documents for this query
            relevant_docs = self.relevance_judgments[query_id]

            # Run the query
            search_results = self.ir_system.search(query_string)
            retrieved_docs = set(result['id'] for result in search_results)

            # Calculate metrics
            metrics = self.calculate_precision_recall(retrieved_docs, relevant_docs)

            # Store detailed results
            results[query_id] = {
                'query': query_string,
                'metrics': metrics,
                'retrieved_docs': list(retrieved_docs),
                'relevant_docs': list(relevant_docs),
                'comments': comments
            }

            # Update sums for averaging
            sum_precision += metrics['precision']
            sum_recall += metrics['recall']
            sum_f1 += metrics['f1']

        # Calculate averages
        num_queries = len(self.test_queries)
        if num_queries > 0:
            results['avg'] = {
                'precision': sum_precision / num_queries,
                'recall': sum_recall / num_queries,
                'f1': sum_f1 / num_queries,
                'num_queries': num_queries
            }

        return results

    def save_evaluation_results(self, results, file_path):
        """Save evaluation results to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Saved evaluation results to {file_path}")

    def print_evaluation_summary(self, results):
        """Print a summary of the evaluation results."""
        print("\n====== IR System Evaluation Summary ======")
        print(f"Number of test queries: {len(self.test_queries)}")

        if 'avg' in results:
            avg = results['avg']
            print("\nAverage metrics across all queries:")
            print(f"  Precision: {avg['precision']:.4f}")
            print(f"  Recall:    {avg['recall']:.4f}")
            print(f"  F1 Score:  {avg['f1']:.4f}")

        print("\nPer-query results:")
        for query_id, query_results in results.items():
            if query_id == 'avg':
                continue

            metrics = query_results['metrics']
            print(f"\nQuery {query_id}: '{query_results['query']}'")
            print(f"  Precision: {metrics['precision']:.4f} ({metrics['relevant_retrieved']}/{metrics['retrieved']})")
            print(f"  Recall:    {metrics['recall']:.4f} ({metrics['relevant_retrieved']}/{metrics['relevant']})")
            print(f"  F1 Score:  {metrics['f1']:.4f}")

            # Print comments for relevant documents if any exist
            if query_results.get('comments'):
                print("  Relevance comments:")
                for doc_id, comment in query_results['comments'].items():
                    doc_id_int = int(doc_id)
                    relevance = "Relevant" if doc_id_int in query_results['relevant_docs'] else "Not relevant"
                    retrieved = "Retrieved" if doc_id_int in query_results['retrieved_docs'] else "Not retrieved"
                    print(f"    Doc {doc_id} ({relevance}, {retrieved}): {comment}")

    def create_test_queries_template(self, output_path="test_queries_template.json"):
        """
        Create a template file for test queries based on the document collection.
        This helps users to create relevance judgments.
        """
        # Get a sample of document info for reference
        sample_docs = []
        for doc_id, doc_info in list(self.ir_system.document_map.items())[:20]:
            sample_docs.append({
                'id': doc_id,
                'artist': doc_info['artist'],
                'filename': doc_info['filename']
            })

        # Create template
        template = {
            'instructions': 'Fill in the queries and mark relevant document IDs for each query',
            'sample_documents': sample_docs,
            'queries': [
                {
                    'id': 'Q1',
                    'query': 'muddy AND waters',
                    'description': 'Documents about Muddy Waters',
                    'relevant_docs': [],
                    'comments': {
                        "sample_doc_id": "Add your judgment notes here - why is this document relevant or not?"
                    }
                },
                {
                    'id': 'Q2',
                    'query': 'chicago AND (guitar OR harmonica)',
                    'description': 'Documents about Chicago blues musicians who play guitar or harmonica',
                    'relevant_docs': [],
                    'comments': {}
                }
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)

        print(f"Created test queries template at {output_path}")
        print("Please fill in the relevant document IDs for each query.")

    def generate_relevance_judgments_tool(self):
        """
        Generate an interactive tool to help create relevance judgments.

        This generates a Python script that can be run separately to help
        create relevance judgments for test queries.
        """
        tool_path = os.path.join(self.results_dir, "create_relevance_judgments.py")

        # Generate the tool script
        with open(tool_path, 'w') as f:
            f.write('''
import os
import json
from blues_ir_system import BluesIRSystem

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Interactive tool to create relevance judgments."""
    # Initialize the IR system
    ir_system = BluesIRSystem()
    ir_system.build_index()
    
    # Load or create queries file
    queries_file = "test_queries.json"
    if os.path.exists(queries_file):
        with open(queries_file, 'r') as f:
            queries = json.load(f)
    else:
        queries = []
    
    while True:
        clear_screen()
        print("===== Relevance Judgments Creation Tool =====\\n")
        print("1. Create a new test query")
        print("2. Edit an existing query")
        print("3. Run a query to find relevant documents")
        print("4. Save and exit")
        print("5. Exit without saving")
        
        choice = input("\\nEnter your choice (1-5): ")
        
        if choice == "1":
            # Create new query
            query_id = input("Enter query ID (e.g., Q1, Q2): ")
            query_string = input("Enter query string: ")
            description = input("Enter query description: ")
            
            # Check if query ID already exists
            if any(q['id'] == query_id for q in queries):
                print(f"Query ID {query_id} already exists!")
                input("Press Enter to continue...")
                continue
            
            queries.append({
                'id': query_id,
                'query': query_string,
                'description': description,
                'relevant_docs': []
            })
            print(f"Added query {query_id}")
            input("Press Enter to continue...")
            
        elif choice == "2":
            # Edit existing query
            if not queries:
                print("No queries to edit!")
                input("Press Enter to continue...")
                continue
                
            print("\\nExisting queries:")
            for i, q in enumerate(queries):
                print(f"{i+1}. [{q['id']}] {q['query']} - {len(q['relevant_docs'])} relevant docs")
            
            try:
                idx = int(input("\\nEnter query number to edit: ")) - 1
                if idx < 0 or idx >= len(queries):
                    print("Invalid query number!")
                    input("Press Enter to continue...")
                    continue
                
                query = queries[idx]
                print(f"\\nEditing query {query['id']}: {query['query']}")
                print("1. Edit query string")
                print("2. Edit description")
                print("3. Edit relevant documents")
                print("4. Edit document comments")
                
                edit_choice = input("\\nEnter your choice (1-4): ")
                
                if edit_choice == "1":
                    query['query'] = input("Enter new query string: ")
                elif edit_choice == "2":
                    query['description'] = input("Enter new description: ")
                elif edit_choice == "3":
                    print(f"Current relevant documents: {query['relevant_docs']}")
                    docs_str = input("Enter new relevant document IDs (comma-separated): ")
                    try:
                        query['relevant_docs'] = [int(docid.strip()) for docid in docs_str.split(',') if docid.strip()]
                    except ValueError:
                        print("Invalid document IDs! Please use comma-separated integers.")
                elif edit_choice == "4":
                    if 'comments' not in query:
                        query['comments'] = {}
                    
                    print("\\nCurrent document comments:")
                    if not query['comments']:
                        print("  (No comments yet)")
                    else:
                        for doc_id, comment in query['comments'].items():
                            print(f"  Doc {doc_id}: {comment}")
                    
                    doc_id = input("\\nEnter document ID to comment on: ")
                    if doc_id:
                        comment = input(f"Enter comment for document {doc_id}: ")
                        query['comments'][doc_id] = comment
                        print(f"Comment added for document {doc_id}")
                
                print(f"Updated query {query['id']}")
                
            except ValueError:
                print("Please enter a number!")
            
            input("Press Enter to continue...")
            
        elif choice == "3":
            # Run a query to find documents
            if not queries:
                print("No queries to run!")
                input("Press Enter to continue...")
                continue
                
            print("\\nExisting queries:")
            for i, q in enumerate(queries):
                print(f"{i+1}. [{q['id']}] {q['query']}")
            
            try:
                idx = int(input("\\nEnter query number to run: ")) - 1
                if idx < 0 or idx >= len(queries):
                    print("Invalid query number!")
                    input("Press Enter to continue...")
                    continue
                
                query = queries[idx]
                print(f"\\nRunning query: {query['query']}")
                
                # Run the query
                results = ir_system.search(query['query'])
                
                if not results:
                    print("No matching documents found.")
                    input("Press Enter to continue...")
                    continue
                
                print(f"\\nFound {len(results)} matching documents:")
                for i, result in enumerate(results):
                    doc_id = result['id']
                    is_relevant = "✓" if doc_id in query['relevant_docs'] else " "
                    print(f"[{is_relevant}] {i+1}. (Doc ID: {doc_id}) {result['artist']} - {result['filename']}")
                
                while True:
                    action = input("\\nToggle relevance (enter document #), view (v#), add comment (c#), or back (b): ")
                    if action.lower() == 'b':
                        break
                    
                    if action.lower().startswith('v'):
                        try:
                            view_idx = int(action[1:]) - 1
                            if 0 <= view_idx < len(results):
                                doc_id = results[view_idx]['id']
                                content = ir_system.get_document_content(doc_id)
                                print("\\n" + "=" * 80)
                                print(f"Document: {results[view_idx]['filename']}")
                                print(f"Artist: {results[view_idx]['artist']}")
                                print("=" * 80)
                                print(content[:500] + "..." if len(content) > 500 else content)
                            else:
                                print("Invalid document number.")
                        except ValueError:
                            print("Please enter a valid format (v1, v2, etc.).")
                    elif action.lower().startswith('c'):
                        try:
                            comment_idx = int(action[1:]) - 1
                            if 0 <= comment_idx < len(results):
                                doc_id = results[comment_idx]['id']
                                if 'comments' not in query:
                                    query['comments'] = {}
                                
                                # Show existing comment if any
                                existing_comment = query['comments'].get(str(doc_id), "")
                                if existing_comment:
                                    print(f"Existing comment: {existing_comment}")
                                
                                # Get new comment
                                comment = input(f"Enter comment for document {doc_id}: ")
                                if comment:
                                    query['comments'][str(doc_id)] = comment
                                    print(f"Comment added for document {doc_id}")
                                elif existing_comment and input("Delete existing comment? (y/n): ").lower() == 'y':
                                    del query['comments'][str(doc_id)]
                                    print(f"Comment deleted for document {doc_id}")
                            else:
                                print("Invalid document number.")
                        except ValueError:
                            print("Please enter a valid format (c1, c2, etc.).")
                    else:
                        try:
                            toggle_idx = int(action) - 1
                            if 0 <= toggle_idx < len(results):
                                doc_id = results[toggle_idx]['id']
                                if doc_id in query['relevant_docs']:
                                    query['relevant_docs'].remove(doc_id)
                                    print(f"Marked document {doc_id} as NOT relevant")
                                else:
                                    query['relevant_docs'].append(doc_id)
                                    print(f"Marked document {doc_id} as relevant")
                                
                                # Update display
                                print(f"\\nFound {len(results)} matching documents:")
                                for i, result in enumerate(results):
                                    doc_id = result['id']
                                    is_relevant = "✓" if doc_id in query['relevant_docs'] else " "
                                    has_comment = "📝" if 'comments' in query and str(doc_id) in query['comments'] else " "
                                    print(f"[{is_relevant}][{has_comment}] {i+1}. (Doc ID: {doc_id}) {result['artist']} - {result['filename']}")
                            else:
                                print("Invalid document number.")
                        except ValueError:
                            print("Please enter a valid number or command.")
                
            except ValueError:
                print("Please enter a number!")
            
            input("Press Enter to continue...")
            
        elif choice == "4":
            # Save and exit
            with open(queries_file, 'w') as f:
                json.dump(queries, f, indent=2)
            print(f"Saved {len(queries)} queries to {queries_file}")
            break
            
        elif choice == "5":
            # Exit without saving
            confirm = input("Are you sure you want to exit without saving? (y/n): ")
            if confirm.lower() == 'y':
                break
        
        else:
            print("Invalid choice!")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
            ''')

        print(f"Generated relevance judgments tool at {tool_path}")
        print(f"Run it with: python {tool_path}")

# Example usage:
if __name__ == "__main__":
    # Initialize the IR system
    ir_system = BluesIRSystem()
    ir_system.build_index()

    # Initialize the evaluator
    evaluator = IRSystemEvaluator(ir_system)

    # Check if test queries file exists
    test_queries_file = "test_queries.json"
    if os.path.exists(test_queries_file):
        # Load existing test queries
        evaluator.load_test_queries_from_file(test_queries_file)

        # Run evaluation
        results = evaluator.evaluate_all_queries()

        # Print and save results
        evaluator.print_evaluation_summary(results)
        evaluator.save_evaluation_results(
            results,
            os.path.join(evaluator.results_dir, "evaluation_results.json")
        )
    else:
        # Create template for test queries
        print("No test queries found. Creating template...")
        evaluator.create_test_queries_template(test_queries_file)

        # Generate tool for creating relevance judgments
        print("Generating tool for creating relevance judgments...")
        evaluator.generate_relevance_judgments_tool()
