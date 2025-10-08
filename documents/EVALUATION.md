# Evaluation Guide

This document explains how to evaluate the AI News Analyst system using the test dataset.

## Quick Start

### Run Full Evaluation (All 20 Examples)

```bash
python evaluate.py
```

This will:
- Evaluate all 20 examples in `data/test_datasets/full_test_set.json`
- Calculate routing accuracy, relevance scores, and correctness scores
- Save results to `data/outputs/evaluation_results.json`
- Display a comprehensive summary

**Note:** Full evaluation may take 10-15 minutes due to LLM judge API calls.

### Run Partial Evaluation (Faster)

To test on a subset for faster iteration:

```bash
# Evaluate first 5 examples
python evaluate.py --num-examples 5

# Evaluate first 10 examples
python evaluate.py --num-examples 10
```

### Custom Options

```bash
# Save results to custom location
python evaluate.py --output results/my_evaluation.json

# Run in quiet mode (less verbose output)
python evaluate.py --quiet

# Combine options
python evaluate.py --num-examples 5 --output quick_results.json --quiet
```

## Evaluation Metrics

The evaluation measures four key dimensions:

### 1. Routing Accuracy
- Measures whether the system correctly routes questions to RAG (recent news) or Wikipedia (general knowledge)
- Calculated as: (Correct Routing Decisions) / (Total Examples) × 100%

### 2. Relevance Score (1-10)
- Uses GPT-4 as a judge to evaluate how relevant the response is to the question
- Scoring:
  - 1-3: Not relevant, off-topic
  - 4-6: Partially relevant
  - 7-8: Mostly relevant
  - 9-10: Highly relevant

### 3. Correctness Score (1-10)
- Uses GPT-4 as a judge to evaluate factual accuracy compared to ground truth
- Scoring:
  - 1-3: Factually incorrect
  - 4-6: Partially correct
  - 7-8: Mostly correct
  - 9-10: Factually accurate

### 4. Performance Metrics
- **Workflow Time**: Time taken to execute the AI workflow (routing + retrieval + generation)
- **Evaluation Time**: Time taken for LLM judge evaluations
- **Total Time**: Combined workflow + evaluation time per example
- **Average Execution Time**: Mean time across all examples
- **Min/Max Time**: Fastest and slowest execution times
- **Total Elapsed Time**: Complete evaluation runtime including overhead

These metrics help identify performance bottlenecks and track improvements over time.

## Test Dataset

The test dataset (`data/test_datasets/full_test_set.json`) contains 20 examples covering:

- **Recent News** (10 examples):
  - Funding announcements
  - Market performance
  - Business deals
  - M&A activity
  - Regulatory changes

- **General Knowledge** (10 examples):
  - Scientific concepts
  - Historical facts
  - Geographic information
  - Biographical information
  - Theoretical concepts

Each example includes:
- `question`: The input question
- `expected_route`: Expected routing decision (rag/wiki)
- `ground_truth`: Reference answer
- `category`: Category of the question

## Understanding Results

### Console Output

During evaluation, you'll see progress for each example:

```
============================================================
Example 1/20
============================================================
Question: What funding did Heidi Health recently raise?
Expected Route: rag
Category: recent_funding

Processing...
✓ Correct routing
  Relevancy score: 9.0/10
  Correctness score: 8.5/10

✓ Example 1 completed
  Route: rag (Expected: rag)
  Relevancy: 9.00/10
  Correctness: 8.50/10
```

### Summary Report

At the end, you'll see a comprehensive summary:

```
============================================================
EVALUATION SUMMARY
============================================================

Total Examples: 20

--- Routing Performance ---
Correct Routing: 18/20
Routing Accuracy: 90.00%

--- Response Quality ---
Average Relevancy Score: 8.25/10
Average Correctness Score: 7.80/10

--- Performance Metrics ---
Average Execution Time: 12.35s per example
Min/Max Execution Time: 8.42s / 18.76s
Total Execution Time: 247.00s
Total Elapsed Time: 252.34s (4.2 minutes)

--- Performance by Category ---

recent_funding:
  Examples: 4
  Routing Accuracy: 100.0%
  Avg Relevancy: 8.50/10
  Avg Correctness: 8.25/10
  Avg Time: 13.24s

general_knowledge:
  Examples: 10
  Routing Accuracy: 90.0%
  Avg Relevancy: 8.00/10
  Avg Correctness: 7.50/10
  Avg Time: 11.85s
```

### Results File

Results are saved in JSON format to `data/outputs/evaluation_results.json`:

```json
{
  "timestamp": "2025-10-06T10:30:00.000000",
  "summary": {
    "total_examples": 20,
    "routing_accuracy": 0.9,
    "avg_relevancy_score": 8.25,
    "avg_correctness_score": 7.80,
    "performance": {
      "avg_execution_time": 12.35,
      "min_execution_time": 8.42,
      "max_execution_time": 18.76,
      "total_execution_time": 247.00,
      "total_elapsed_time": 252.34
    }
  },
  "detailed_results": [
    {
      "example_id": 0,
      "question": "What funding did Heidi Health recently raise?",
      "expected_route": "rag",
      "actual_route": "rag",
      "routing_correct": true,
      "response": "Heidi Health raised...",
      "ground_truth": "Heidi Health, a Melbourne-based company...",
      "relevancy_score": 9.0,
      "correctness_score": 8.5,
      "category": "recent_funding",
      "timing": {
        "workflow_time": 10.24,
        "evaluation_time": 3.11,
        "total_time": 13.35
      }
    }
  ]
}
```

## Troubleshooting

### API Rate Limits

If you encounter OpenAI API rate limits:
1. Use `--num-examples` to evaluate fewer examples at a time
2. Add delays between API calls (modify `evaluate.py` if needed)
3. Check your OpenAI API tier and rate limits

### Missing Environment Variables

Ensure your `.env` file contains:
```
OPENAI_API_KEY=your_api_key_here
```

### ChromaDB Issues

If you get ChromaDB errors, the vector database might not be initialized:
1. Run the data ingestion pipeline first
2. Check that `data/vector_db/` contains the database files

## Performance Targets

Good performance benchmarks:

### Quality Metrics
- **Routing Accuracy**: > 90%
- **Relevancy Score**: > 7.5/10
- **Correctness Score**: > 7.0/10

### Performance Metrics
- **Average Execution Time**: < 15s per example
- **Workflow Time**: < 10s (routing + retrieval + generation)
- **Evaluation Time**: < 5s (LLM judge calls)

Use timing data to identify optimization opportunities:
- Slow routing decisions → optimize route decision logic
- Slow retrieval → optimize vector search or Wikipedia API calls
- Slow generation → consider faster LLM models or better prompts

## Next Steps

After evaluation, you can:
1. **Analyze failing examples** to identify patterns
2. **Optimize performance** using timing data:
   - Identify slowest components (routing, retrieval, generation)
   - Compare execution times across categories
   - Track performance improvements over time
3. **Adjust routing logic** in `src/workflow/news_analysis_workflow.py`
4. **Fine-tune prompts** for better responses
5. **Add more test examples** to expand coverage
6. **Re-run evaluation** to measure improvements

### Tracking Improvements Over Time

Save evaluation results with descriptive filenames to track progress:

```bash
# Baseline evaluation
python evaluate.py --output results/baseline_v1.json

# After optimization
python evaluate.py --output results/optimized_v2.json

# Compare results
# Check timing improvements, quality changes, etc.
```

Compare `performance` metrics across runs to validate optimizations.

