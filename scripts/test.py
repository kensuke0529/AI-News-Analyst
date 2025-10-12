import re

def routing_accuracy(i, result, test_dataset, metrics):
    """
    Evaluate routing accuracy for a single example.
    """
    is_correct = result.get('route_choice') == test_dataset[i].get('expected_route')
    
    if is_correct:
        print('Correct routing')
    else:
        print(f'Incorrect routing: got {result.get("route_choice")}, expected {test_dataset[i].get("expected_route")}')
    metrics['routing_correct'] = is_correct
    return metrics


def _extract_number(text):
    """
    Extract the first number (1–10) from a text string.
    """
    text = str(getattr(text, 'content', text)).strip()
    match = re.search(r'\b(\d+(?:\.\d+)?)\b', text)
    if not match:
        return 0.0
    num = float(match.group(1))
    return max(1.0, min(10.0, num))  # clamp to 1–10


def judge_relevance(i, result, test_dataset, metrics, llm_judge):
    """
    Evaluate response relevance using an LLM judge (pure number output).
    """
    question = test_dataset[i].get('question', '')
    generated = result.get('response', '')
    truth = test_dataset[i].get('ground_truth', '')

    relevancy_prompt = f"""You are an AI judge evaluating response relevancy.
Rate how relevant the generated response is to the question and the ground truth.

Question: {question}
Generated Response: {generated}
Ground Truth: {truth}

Provide a score from 1–10 where:
1–3: Not relevant
4–6: Partially relevant
7–8: Mostly relevant
9–10: Fully relevant

Examples:
Q: "What is the capital of France?"
Generated: "The capital is Berlin."
Truth: "Paris"
→ 2

Q: "Who wrote Hamlet?"
Generated: "Shakespeare wrote Hamlet."
Truth: "William Shakespeare"
→ 10

Respond ONLY with a single number between 1 and 10. No words, no punctuation.
"""

    try:
        judge_raw = llm_judge.invoke(relevancy_prompt)
        judge_score = _extract_number(judge_raw)
    except Exception as e:
        print(f"Error in relevance judging: {e}")
        judge_score = 0.0

    print(f"  Relevancy score: {judge_score}/10")
    metrics['relevancy_score'] = judge_score
    return metrics


def judge_correctness(i, result, test_dataset, metrics, llm_judge2):
    """
    Evaluate factual correctness using an LLM judge (pure number output).
    """
    question = test_dataset[i].get('question', '')
    generated = result.get('response', '')
    truth = test_dataset[i].get('ground_truth', '')

    correctness_prompt = f"""You are an expert fact checker.
Compare the generated response to the ground truth and rate factual accuracy.

Question: {question}
Ground Truth: {truth}
Generated Response: {generated}

Provide a score from 1–10 where:
1–3: Factually incorrect
4–6: Partially correct
7–8: Mostly correct
9–10: Fully correct

Respond ONLY with a single number between 1 and 10. No text or explanation.
"""

    try:
        judge_raw2 = llm_judge2.invoke(correctness_prompt)
        correctness_score = _extract_number(judge_raw2)
    except Exception as e:
        print(f"Error in correctness judging: {e}")
        correctness_score = 0.0

    print(f"  Correctness score: {correctness_score}/10")
    metrics['correctness_score'] = correctness_score
    return metrics
