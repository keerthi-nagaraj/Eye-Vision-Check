import time
from config import DISPLAY_TIME
from question_generator import generate_sequence


class ShapeMemoryTest:
    def __init__(self):
        self.correct_answers = 0
        self.total_questions = 0

    def run_question(self, level):
        """Run a single question of given difficulty level.

        The `generate_sequence` function creates a random sequence of shape IDs.
        The sequence is shown for DISPLAY_TIME seconds, then cleared from the screen.
        The user inputs their answer which is compared to the original sequence.
        """
        sequence = generate_sequence(level)

        print("\nRemember this sequence:")
        print(*sequence)

        time.sleep(DISPLAY_TIME)

        # Clear the console output by printing newlines
        print("\n" * 50)

        answer = input("Enter sequence: ")

        try:
            user_sequence = [int(x) for x in answer.split()]
        except ValueError:
            user_sequence = []

        self.total_questions += 1

        if user_sequence == sequence:
            self.correct_answers += 1
            print("✓ Correct")
        else:
            print("✗ Wrong")
            print("Correct Sequence:", sequence)
