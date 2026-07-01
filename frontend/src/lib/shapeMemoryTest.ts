// src/lib/shapeMemoryTest.ts
export const DISPLAY_TIME = 3; // seconds
export const TOTAL_QUESTIONS = 5;
export const SHAPES: Record<number, string> = {
  1: "Square",
  2: "Circle",
  3: "Triangle",
  4: "Star",
  5: "Diamond",
  6: "Heart"
};

export function generateSequence(length = 3): number[] {
  const seq: number[] = [];
  for (let i = 0; i < length; i++) {
    seq.push(Math.floor(Math.random() * 6) + 1); // 1-6 inclusive
  }
  return seq;
}

export interface Result {
  accuracy: number;
  category: string;
  recommendation: string;
}

export function generateResult(correct: number, total: number): Result {
  const accuracy = total ? (correct / total) * 100 : 0;
  let category = "NEEDS IMPROVEMENT";
  let recommendation = "Consider memory training exercises.";
  if (accuracy >= 90) {
    category = "EXCELLENT";
    recommendation = "Excellent visual memory.";
  } else if (accuracy >= 70) {
    category = "GOOD";
    recommendation = "Good visual memory.";
  } else if (accuracy >= 50) {
    category = "AVERAGE";
    recommendation = "Visual memory can be improved.";
  }
  return { accuracy, category, recommendation };
}
