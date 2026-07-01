export function generateNumber(): number {
	const numbers = [12, 8, 6, 3, 0];
	return numbers[Math.floor(Math.random() * numbers.length)];
}

export function validateAnswer(userAnswer: string, correctNumber: number): boolean {
	if (correctNumber === 0) {
		return userAnswer.toLowerCase() === 'none' || userAnswer.toLowerCase() === 'no number';
	}
	return parseInt(userAnswer) === correctNumber;
}

export function calculateColorBlindnessRisk(correctAnswers: number, totalQuestions: number): {
	risk: 'low' | 'moderate' | 'high';
	percentage: number;
	diagnosis: string;
} {
	const percentage = (correctAnswers / totalQuestions) * 100;
	
	let risk: 'low' | 'moderate' | 'high';
	let diagnosis: string;
	
	if (percentage >= 80) {
		risk = 'low';
		diagnosis = 'Normal color vision detected';
	} else if (percentage >= 60) {
		risk = 'moderate';
		diagnosis = 'Mild color vision deficiency possible';
	} else if (percentage >= 40) {
		risk = 'moderate';
		diagnosis = 'Moderate color vision deficiency likely';
	} else {
		risk = 'high';
		diagnosis = 'Significant color vision deficiency detected';
	}
	
	return { risk, percentage, diagnosis };
}

export function getColorBlindnessType(correctAnswers: number, totalQuestions: number): {
	type: 'normal' | 'protanopia' | 'deuteranopia' | 'tritanopia';
	description: string;
} {
	const percentage = (correctAnswers / totalQuestions) * 100;
	
	// This is a simplified analysis - real diagnosis requires professional testing
	if (percentage >= 80) {
		return {
			type: 'normal',
			description: 'Normal color vision'
		};
	} else if (percentage >= 60) {
		return {
			type: 'deuteranopia',
			description: 'Possible green color blindness (deuteranopia)'
		};
	} else if (percentage >= 40) {
		return {
			type: 'protanopia',
			description: 'Possible red color blindness (protanopia)'
		};
	} else {
		return {
			type: 'tritanopia',
			description: 'Possible blue color blindness (tritanopia)'
		};
	}
}

export function generateTestPlates(): Array<{
	number: number;
	expected: string;
	difficulty: 'easy' | 'medium' | 'hard';
}> {
	return [
		{ number: 12, expected: '12', difficulty: 'easy' },
		{ number: 8, expected: '8', difficulty: 'easy' },
		{ number: 6, expected: '6', difficulty: 'medium' },
		{ number: 3, expected: '3', difficulty: 'medium' },
		{ number: 0, expected: 'No number', difficulty: 'hard' }
	];
}

export function formatTestResults(results: Array<{
	plate: number;
	expected: string;
	userAnswer: string;
	correct: boolean;
}>): {
	score: number;
	total: number;
	percentage: number;
	diagnosis: string;
	recommendations: string[];
} {
	const correct = results.filter(r => r.correct).length;
	const total = results.length;
	const percentage = (correct / total) * 100;
	
	const { diagnosis } = calculateColorBlindnessRisk(correct, total);
	
	const recommendations: string[] = [];
	
	if (percentage >= 80) {
		recommendations.push('Your color vision appears to be normal');
		recommendations.push('No further action needed at this time');
	} else if (percentage >= 60) {
		recommendations.push('Consider consulting an eye care professional');
		recommendations.push('You may benefit from professional color vision testing');
	} else {
		recommendations.push('Consult an eye care professional for comprehensive testing');
		recommendations.push('Consider color vision accommodations if needed');
		recommendations.push('Professional diagnosis recommended');
	}
	
	return {
		score: correct,
		total,
		percentage,
		diagnosis,
		recommendations
	};
}