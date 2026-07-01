def generate_result(correct, total):
    """Calculate accuracy and provide a category and recommendation.

    Args:
        correct (int): Number of correct answers.
        total (int): Total number of questions.
    Returns:
        dict: Dictionary with accuracy, category, and recommendation.
    """
    accuracy = (correct / total) * 100 if total else 0

    if accuracy >= 90:
        category = "EXCELLENT"
        recommendation = "Excellent visual memory."
    elif accuracy >= 70:
        category = "GOOD"
        recommendation = "Good visual memory."
    elif accuracy >= 50:
        category = "AVERAGE"
        recommendation = "Visual memory can be improved."
    else:
        category = "NEEDS IMPROVEMENT"
        recommendation = "Consider memory training exercises."

    return {
        "accuracy": accuracy,
        "category": category,
        "recommendation": recommendation,
    }
