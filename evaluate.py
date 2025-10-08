#!/usr/bin/env python3
"""
AI News Analyst - Evaluation Script

This script evaluates the news analysis workflow on a test dataset,
measuring routing accuracy, relevance, and correctness.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.workflow.news_analysis_workflow import app
from test import routing_accuracy, judge_relevance, judge_correctness
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Initialize LLM judge
llm_judge = ChatOpenAI(model='gpt-4o', api_key=openai_api_key, temperature=0)


def run_evaluation(dataset_path: str, num_examples: int = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Run evaluation on the test dataset.
    
    Args:
        dataset_path: Path to the test dataset JSON file
        num_examples: Number of examples to evaluate (None for all)
        verbose: Whether to print detailed progress
        
    Returns:
        Dictionary containing evaluation results and metrics
    """
    # Load test dataset
    with open(dataset_path, "r") as f:
        dataset_json = json.load(f)
    
    # Handle both old and new format
    if isinstance(dataset_json, dict) and 'test_cases' in dataset_json:
        # New format with test_cases and metadata
        test_dataset = dataset_json['test_cases']
        dataset_metadata = dataset_json.get('metadata', {})
    else:
        # Old format - direct array
        test_dataset = dataset_json
        dataset_metadata = {}
    
    if num_examples is not None:
        test_dataset = test_dataset[:num_examples]
    
    total_examples = len(test_dataset)
    print(f"\n{'='*60}")
    print(f"Starting Evaluation on {total_examples} examples")
    if dataset_metadata:
        print(f"Dataset: {dataset_metadata.get('date_created', 'Unknown date')}")
        print(f"RAG Questions: {dataset_metadata.get('rag_questions', 'N/A')}, Wiki Questions: {dataset_metadata.get('wiki_questions', 'N/A')}")
    print(f"{'='*60}\n")
    
    # Initialize metrics
    metrics = {
        'correct_routing': 0,
        'total_examples': total_examples,
        'relevancy_scores': [],
        'correctness_scores': [],
        'execution_times': [],
        'results_by_example': [],
        'total_start_time': time.time()
    }
    
    # Run evaluation on each example
    for i, example in enumerate(test_dataset):
        if verbose:
            print(f"\n{'='*60}")
            print(f"Example {i+1}/{total_examples} - ID: {example.get('id', f'example_{i}')}")
            print(f"{'='*60}")
            print(f"Question: {example['question']}")
            print(f"Expected Route: {example['expected_route']}")
            print(f"Category: {example['category']} | Difficulty: {example.get('difficulty', 'N/A')}")
            print(f"\n{'Processing...'}")
        
        try:
            # Measure workflow execution time
            workflow_start = time.time()
            result = app.invoke({"prompt": example['question']})
            workflow_time = time.time() - workflow_start
            
            # Store individual example metrics
            example_metrics = {}
            
            # Measure evaluation time
            eval_start = time.time()
            
            # Evaluate routing accuracy
            routing_accuracy(i, result, test_dataset, example_metrics)
            
            # Judge relevance
            judge_relevance(i, result, test_dataset, example_metrics, llm_judge)
            
            # Judge correctness
            judge_correctness(i, result, test_dataset, example_metrics, llm_judge)
            
            eval_time = time.time() - eval_start
            total_time = workflow_time + eval_time
            
            # Update global metrics
            if 'routing_correct' in example_metrics and example_metrics.get('routing_correct', False):
                metrics['correct_routing'] += 1
            
            metrics['relevancy_scores'].append(example_metrics.get('relevancy_score', 0))
            metrics['correctness_scores'].append(example_metrics.get('correctness_score', 0))
            metrics['execution_times'].append(total_time)
            
            # Store detailed results
            metrics['results_by_example'].append({
                'test_id': example.get('id', f'example_{i}'),
                'example_index': i,
                'question': example['question'],
                'expected_route': example['expected_route'],
                'actual_route': result.get('route_choice', 'unknown'),
                'routing_correct': result.get('route_choice') == example['expected_route'],
                'response': result.get('response', ''),
                'ground_truth': example['ground_truth'],
                'relevancy_score': example_metrics.get('relevancy_score', 0),
                'correctness_score': example_metrics.get('correctness_score', 0),
                'category': example['category'],
                'difficulty': example.get('difficulty', 'N/A'),
                'relevant_doc_ids': example.get('relevant_doc_ids', []),
                'timing': {
                    'workflow_time': round(workflow_time, 2),
                    'evaluation_time': round(eval_time, 2),
                    'total_time': round(total_time, 2)
                }
            })
            
            if verbose:
                print(f"\n✓ Example {i+1} completed")
                print(f"  Route: {result.get('route_choice', 'unknown')} (Expected: {example['expected_route']})")
                print(f"  Relevancy: {example_metrics.get('relevancy_score', 0):.2f}/10")
                print(f"  Correctness: {example_metrics.get('correctness_score', 0):.2f}/10")
                print(f"  Time: {workflow_time:.2f}s (workflow) + {eval_time:.2f}s (eval) = {total_time:.2f}s total")
        
        except Exception as e:
            print(f"\n✗ Error processing example {i+1}: {str(e)}")
            metrics['results_by_example'].append({
                'test_id': example.get('id', f'example_{i}'),
                'example_index': i,
                'question': example['question'],
                'category': example['category'],
                'difficulty': example.get('difficulty', 'N/A'),
                'error': str(e)
            })
    
    # Calculate final metrics
    total_elapsed = time.time() - metrics['total_start_time']
    
    metrics['routing_accuracy'] = metrics['correct_routing'] / total_examples
    metrics['avg_relevancy_score'] = sum(metrics['relevancy_scores']) / len(metrics['relevancy_scores']) if metrics['relevancy_scores'] else 0
    metrics['avg_correctness_score'] = sum(metrics['correctness_scores']) / len(metrics['correctness_scores']) if metrics['correctness_scores'] else 0
    
    # Performance metrics
    if metrics['execution_times']:
        metrics['avg_execution_time'] = sum(metrics['execution_times']) / len(metrics['execution_times'])
        metrics['min_execution_time'] = min(metrics['execution_times'])
        metrics['max_execution_time'] = max(metrics['execution_times'])
        metrics['total_execution_time'] = sum(metrics['execution_times'])
    else:
        metrics['avg_execution_time'] = 0
        metrics['min_execution_time'] = 0
        metrics['max_execution_time'] = 0
        metrics['total_execution_time'] = 0
    
    metrics['total_elapsed_time'] = total_elapsed
    
    # Remove temporary tracking data
    del metrics['total_start_time']
    
    return metrics


def print_summary(metrics: Dict[str, Any]):
    """Print evaluation summary."""
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"\nTotal Examples: {metrics['total_examples']}")
    print(f"\n--- Routing Performance ---")
    print(f"Correct Routing: {metrics['correct_routing']}/{metrics['total_examples']}")
    print(f"Routing Accuracy: {metrics['routing_accuracy']*100:.2f}%")
    print(f"\n--- Response Quality ---")
    print(f"Average Relevancy Score: {metrics['avg_relevancy_score']:.2f}/10")
    print(f"Average Correctness Score: {metrics['avg_correctness_score']:.2f}/10")
    print(f"\n--- Performance Metrics ---")
    print(f"Average Execution Time: {metrics['avg_execution_time']:.2f}s per example")
    print(f"Min/Max Execution Time: {metrics['min_execution_time']:.2f}s / {metrics['max_execution_time']:.2f}s")
    print(f"Total Execution Time: {metrics['total_execution_time']:.2f}s")
    print(f"Total Elapsed Time: {metrics['total_elapsed_time']:.2f}s ({metrics['total_elapsed_time']/60:.1f} minutes)")
    
    # Category breakdown
    print(f"\n--- Performance by Category ---")
    category_stats = {}
    for result in metrics['results_by_example']:
        if 'error' in result:
            continue
        category = result['category']
        if category not in category_stats:
            category_stats[category] = {
                'count': 0,
                'routing_correct': 0,
                'relevancy_sum': 0,
                'correctness_sum': 0
            }
        category_stats[category]['count'] += 1
        if result['routing_correct']:
            category_stats[category]['routing_correct'] += 1
        category_stats[category]['relevancy_sum'] += result['relevancy_score']
        category_stats[category]['correctness_sum'] += result['correctness_score']
    
    # Calculate timing by category
    category_times = {}
    for result in metrics['results_by_example']:
        if 'error' in result:
            continue
        category = result['category']
        if category not in category_times:
            category_times[category] = []
        category_times[category].append(result['timing']['total_time'])
    
    for category, stats in sorted(category_stats.items()):
        avg_time = sum(category_times.get(category, [0])) / len(category_times.get(category, [1]))
        print(f"\n{category}:")
        print(f"  Examples: {stats['count']}")
        print(f"  Routing Accuracy: {stats['routing_correct']/stats['count']*100:.1f}%")
        print(f"  Avg Relevancy: {stats['relevancy_sum']/stats['count']:.2f}/10")
        print(f"  Avg Correctness: {stats['correctness_sum']/stats['count']:.2f}/10")
        print(f"  Avg Time: {avg_time:.2f}s")
    
    # Difficulty breakdown
    print(f"\n--- Performance by Difficulty ---")
    difficulty_stats = {}
    for result in metrics['results_by_example']:
        if 'error' in result:
            continue
        difficulty = result.get('difficulty', 'N/A')
        if difficulty not in difficulty_stats:
            difficulty_stats[difficulty] = {
                'count': 0,
                'routing_correct': 0,
                'relevancy_sum': 0,
                'correctness_sum': 0
            }
        difficulty_stats[difficulty]['count'] += 1
        if result['routing_correct']:
            difficulty_stats[difficulty]['routing_correct'] += 1
        difficulty_stats[difficulty]['relevancy_sum'] += result['relevancy_score']
        difficulty_stats[difficulty]['correctness_sum'] += result['correctness_score']
    
    difficulty_order = ['easy', 'medium', 'hard', 'N/A']
    for difficulty in difficulty_order:
        if difficulty not in difficulty_stats:
            continue
        stats = difficulty_stats[difficulty]
        print(f"\n{difficulty.capitalize()}:")
        print(f"  Examples: {stats['count']}")
        print(f"  Routing Accuracy: {stats['routing_correct']/stats['count']*100:.1f}%")
        print(f"  Avg Relevancy: {stats['relevancy_sum']/stats['count']:.2f}/10")
        print(f"  Avg Correctness: {stats['correctness_sum']/stats['count']:.2f}/10")
    
    print(f"\n{'='*60}\n")


def save_results(metrics: Dict[str, Any], output_path: str):
    """Save evaluation results to JSON file."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_examples': metrics['total_examples'],
            'routing_accuracy': metrics['routing_accuracy'],
            'avg_relevancy_score': metrics['avg_relevancy_score'],
            'avg_correctness_score': metrics['avg_correctness_score'],
            'performance': {
                'avg_execution_time': round(metrics['avg_execution_time'], 2),
                'min_execution_time': round(metrics['min_execution_time'], 2),
                'max_execution_time': round(metrics['max_execution_time'], 2),
                'total_execution_time': round(metrics['total_execution_time'], 2),
                'total_elapsed_time': round(metrics['total_elapsed_time'], 2)
            }
        },
        'detailed_results': metrics['results_by_example']
    }
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_path}")


def main():
    """Main evaluation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate AI News Analyst')
    parser.add_argument('--dataset', type=str, default='data/evaluation/expanded_test_set.json',
                        help='Path to test dataset JSON file')
    parser.add_argument('--num-examples', type=int, default=None,
                        help='Number of examples to evaluate (default: all)')
    parser.add_argument('--output', type=str, default='data/outputs/evaluation_results_expanded.json',
                        help='Path to save evaluation results')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress detailed progress output')
    
    args = parser.parse_args()
    
    # Resolve dataset path
    dataset_path = os.path.join(os.path.dirname(__file__), args.dataset)
    
    # Run evaluation
    metrics = run_evaluation(
        dataset_path=dataset_path,
        num_examples=args.num_examples,
        verbose=not args.quiet
    )
    
    # Print summary
    print_summary(metrics)
    
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_results(metrics, output_path)


if __name__ == "__main__":
    main()

