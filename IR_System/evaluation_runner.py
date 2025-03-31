#!/usr/bin/env python
"""
Evaluation Runner for Blues IR System
-------------------------------------
This script runs a full evaluation of the Boolean IR system using precision and recall metrics.
It can be used to compare different versions of the system or different preprocessing techniques.
"""

import os
import json
import nltk
import argparse
from datetime import datetime
from blues_ir_system import BluesIRSystem
from ir_evaluation import IRSystemEvaluator

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading required NLTK resources...")
    nltk.download('punkt')
    nltk.download('stopwords')

def run_evaluation(test_queries_file, output_dir=None):
    """Run a full evaluation using the specified test queries file."""
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the IR system
    print("Initializing IR system...")
    ir_system = BluesIRSystem()
    ir_system.build_index()
    
    # Initialize the evaluator
    print("Setting up evaluator...")
    evaluator = IRSystemEvaluator(ir_system)
    
    # Load test queries
    print(f"Loading test queries from {test_queries_file}...")
    evaluator.load_test_queries_from_file(test_queries_file)
    
    # Run evaluation
    print("Running evaluation...")
    results = evaluator.evaluate_all_queries()
    
    # Print summary
    evaluator.print_evaluation_summary(results)
    
    # Save results
    if output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(output_dir, f"evaluation_results_{timestamp}.json")
        evaluator.save_evaluation_results(results, results_file)
        print(f"Results saved to {results_file}")
    
    return results

def generate_test_data():
    """Generate template and tools for creating test data."""
    print("Initializing IR system...")
    ir_system = BluesIRSystem()
    ir_system.build_index()
    
    print("Setting up evaluator...")
    evaluator = IRSystemEvaluator(ir_system)
    
    # Create test queries template
    template_file = "test_queries_template.json"
    print(f"Creating test queries template at {template_file}...")
    evaluator.create_test_queries_template(template_file)
    
    # Generate relevance judgments tool
    print("Generating relevance judgments tool...")
    evaluator.generate_relevance_judgments_tool()
    
    print("\nSetup complete! You can now:")
    print(f"1. Edit {template_file} to create your test queries")
    print("2. Run the relevance judgments tool to mark relevant documents")
    print("3. Run this script again with the evaluation command")

def main():
    parser = argparse.ArgumentParser(description="Evaluate the Blues IR System")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Generate test data files and tools")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Run evaluation")
    eval_parser.add_argument(
        "--queries", "-q",
        default="test_queries.json",
        help="Path to test queries JSON file"
    )
    eval_parser.add_argument(
        "--output-dir", "-o",
        default="evaluation_results",
        help="Directory to save evaluation results"
    )
    
    args = parser.parse_args()
    
    if args.command == "setup":
        generate_test_data()
    elif args.command == "evaluate":
        run_evaluation(args.queries, args.output_dir)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
