export type TestType = 'ishihara' | 'tritan' | 'hue' | 'webcam' | 'amsler';

export interface TestResult {
	id: string;
	testType: TestType | string;
	result: string;
	score: number;
	timestamp: string;
	details?: unknown;
	totalQuestions?: number;
	correctAnswers?: number;
	testData?: Record<string, unknown>;
	difficulty?: string;
	diagnosis?: string;
	userId?: string;
}

export type TestResultInput = Omit<TestResult, 'id' | 'timestamp'> & { userId?: string };

export interface DistortionMark {
	x: number;
	y: number;
}

export interface UserSettings {
	name: string;
	age: number;
	notifications: boolean;
	darkMode: boolean;
}

export interface ResultsStats {
	totalResults: number;
	ishiharaCount: number;
	tritanCount: number;
	hueCount: number;
	webcamCount: number;
	amslerCount: number;
	contrastCount?: number;
}
