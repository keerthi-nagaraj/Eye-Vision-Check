from memory_test import ShapeMemoryTest
from results import generate_result
from config import SHAPES, TOTAL_QUESTIONS


def show_mapping():
    print("\n=================================")
    print("SHAPE MEMORY TEST")
    print("=================================\n")
    print("Shape Mapping\n")
    for num, shape in SHAPES.items():
        print(f"{num} = {shape}")
    input("\nPress Enter to Start...")


def main():
    show_mapping()
    test = ShapeMemoryTest()
    for i in range(TOTAL_QUESTIONS):
        if i < 3:
            level = 3
        elif i < 7:
            level = 4
        else:
            level = 5
        print(f"\nQuestion {i + 1}/{TOTAL_QUESTIONS}")
        test.run_question(level)
    result = generate_result(test.correct_answers, test.total_questions)
    print("\n=================================")
    print("FINAL RESULT")
    print("=================================")
    print(f"Questions       : {test.total_questions}")
    print(f"Correct Answers : {test.correct_answers}")
    print(f"Wrong Answers   : {test.total_questions - test.correct_answers}")
    print(f"Accuracy        : {result['accuracy']:.1f}%")
    print(f"Category        : {result['category']}")
    print("\nRecommendation:")
    print(result["recommendation"])


if __name__ == "__main__":
    main()
