def routing_accuracy(i, result, test_dataset, metrics):
    """
    Evaluate routing accuracy for a single example.
    
    Args:
        i: Index of the current test example
        result: Result from the workflow containing route_choice
        test_dataset: List of test examples
        metrics: Dictionary to store metrics
    
    Returns:
        Updated metrics dictionary
    """
    is_correct = result.get('route_choice') == test_dataset[i]['expected_route']
    
    if is_correct:
        print('✓ Correct routing')
    else:
        print(f'✗ Incorrect routing: got {result.get("route_choice")}, expected {test_dataset[i]["expected_route"]}')
    
    # Store routing correctness for this example
    metrics['routing_correct'] = is_correct
    
    return metrics

def judge_relevance(i, result, test_dataset, metrics, llm_judge):
    """
    Evaluate response relevance using an LLM judge.
    
    Args:
        i: Index of the current test example
        result: Result from the workflow containing the response
        test_dataset: List of test examples
        metrics: Dictionary to store metrics
        llm_judge: LLM instance to use as a judge
    
    Returns:
        Updated metrics dictionary
    """
    question = test_dataset[i]['question']
    generated = result.get('response', '')
    truth = test_dataset[i]['ground_truth']

    relevancy_prompt = f"""You are an AI judge evaluating response relevancy.
Based on the question, generated response, and ground truth, rate how relevant and related the generated response is to answering the question and aligning with the ground truth.

Question: {question}
Generated Response: {generated}
Ground Truth: {truth}

Provide a score from 1-10 where:
- 1-3: Not relevant, off-topic or incorrect focus
- 4-6: Partially relevant, missing key information
- 7-8: Mostly relevant, covers the main points
- 9-10: Highly relevant, comprehensive and accurate

Respond with ONLY a number between 1 and 10."""

    try:
        judge_raw = llm_judge.invoke(relevancy_prompt)
        judge_text = getattr(judge_raw, 'content', str(judge_raw)).strip()
        
        # Extract score
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', judge_text)
        judge_score = float(match.group(1)) if match else 0.0
        
        # Clamp score to 0-10 range
        judge_score = max(0.0, min(10.0, judge_score))
        
    except Exception as e:
        print(f"Error in relevance judging: {e}")
        judge_score = 0.0

    print(f"  Relevancy score: {judge_score}/10")
    metrics['relevancy_score'] = judge_score
    
    return metrics

def judge_correctness(i, result, test_dataset, metrics, llm_judge2):
    """
    Evaluate factual correctness using an LLM judge.
    
    Args:
        i: Index of the current test example
        result: Result from the workflow containing the response
        test_dataset: List of test examples
        metrics: Dictionary to store metrics
        llm_judge2: LLM instance to use as a judge
    
    Returns:
        Updated metrics dictionary
    """
    question = test_dataset[i]['question']
    generated = result.get('response', '')
    truth = test_dataset[i]['ground_truth']
    
    correctness_prompt = f"""You are an expert fact checker evaluating factual accuracy.
Compare the generated response to the ground truth and evaluate how factually correct it is.

Question: {question}
Ground Truth: {truth}
Generated Response: {generated}

Provide a score from 1-10 where:
- 1-3: Factually incorrect, contains wrong information
- 4-6: Partially correct, missing important facts
- 7-8: Mostly correct, minor inaccuracies or omissions
- 9-10: Factually accurate and complete

Respond with ONLY a number between 1 and 10."""
    
    try:
        correctness_raw = llm_judge2.invoke(correctness_prompt)
        correctness_text = getattr(correctness_raw, 'content', str(correctness_raw)).strip()
        
        # Extract score
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', correctness_text)
        correctness_score = float(match.group(1)) if match else 0.0
        
        # Clamp score to 0-10 range
        correctness_score = max(0.0, min(10.0, correctness_score))
        
    except Exception as e:
        print(f"Error in correctness judging: {e}")
        correctness_score = 0.0

    print(f"  Correctness score: {correctness_score}/10")
    metrics['correctness_score'] = correctness_score
    
    return metrics
