import random

def generate_sequence(length=3):
    """Generate a random sequence of shape IDs.

    Args:
        length (int): Number of shapes in the sequence.
    Returns:
        List[int]: List of random integers between 1 and 6 inclusive.
    """
    return [random.randint(1, 6) for _ in range(length)]
