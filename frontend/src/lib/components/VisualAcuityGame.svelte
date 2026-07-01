<script lang="ts">
// ==========================
// TYPES
// ==========================

interface CurrentTarget {
	display: string;
	answer: string;
	size: number;
	sizeGroup: 'large' | 'medium' | 'small';
	shownAt: number;
}

interface Question {
	display: string;
	answer: string;
	size: number;
	sizeGroup: 'large' | 'medium' | 'small';
	category: 'letter' | 'number' | 'word' | 'shape' | 'object';
}

interface SizeGroupStats {
	total: number;
	correct: number;
	incorrect: number;
	accuracy: number;
}

interface TestResult {
	totalQuestions: number;
	correctAnswers: number;
	incorrectAnswers: number;
	overallAccuracy: number;
	large: SizeGroupStats;
	medium: SizeGroupStats;
	small: SizeGroupStats;
	averageResponseTime: number;
	visionCategory: string;
	recommendations: string[];
}

// ==========================
// CONFIGURABLE SCORING PARAMETERS
// ==========================

// Accuracy thresholds (percentage)
const ACCURACY_THRESHOLD_LOW = 70; // Threshold for detecting vision issues
const ACCURACY_THRESHOLD_OVERALL = 85; // Overall accuracy for normal vision
const ACCURACY_THRESHOLD_HIGH = 80; // High accuracy threshold for normal vision

// Error count thresholds
const ERROR_COUNT_HIGH = 4; // High error count indicating vision issues
const ERROR_COUNT_LOW_LARGE = 2; // Acceptable error count for large items
const ERROR_COUNT_LOW_MEDIUM = 2; // Acceptable error count for medium items
const ERROR_COUNT_LOW_SMALL = 3; // Acceptable error count for small items

// Score point values for vision category scoring
const SCORE_HIGH_ISSUE = 3; // Points for major vision issue indicators
const SCORE_MODERATE_ISSUE = 2; // Points for moderate vision issue indicators
const SCORE_MINOR_ISSUE = 1; // Points for minor vision issue indicators
const SCORE_NORMAL_HIGH = 4; // Points for strong normal vision indicators
const SCORE_NORMAL_MEDIUM = 3; // Points for good normal vision indicators
const SCORE_NORMAL_LOW = 2; // Points for acceptable normal vision indicators

// Combined vision issues cutoff
const COMBINED_VISION_CUTOFF = 3; // Minimum score to indicate combined vision issues

// Recommendation thresholds
const RECOMMENDATION_THRESHOLD_LOW = 60; // Threshold for generating specific recommendations
const RECOMMENDATION_THRESHOLD_EXCELLENT = 85; // Threshold for excellent performance recommendation

// WebSocket configuration
const WEBSOCKET_URL = 'ws://localhost:8765'; // WebSocket server URL
const WEBSOCKET_RECONNECT_DELAY = 3000; // Reconnection delay in milliseconds
const DISTANCE_ROUNDING_FACTOR = 10; // Factor for rounding distance calculations

// Distance measurement configuration
const CONSECUTIVE_MEASUREMENTS_THRESHOLD = 5; // Number of consecutive measurements to update display status

// Test configuration
const QUESTIONS_PER_SIZE_GROUP = 5; // Number of questions per size group (large, medium, small)
const QUESTION_TIMER_DURATION = 5000; // Time limit for each question in milliseconds
const PERCENTAGE_MULTIPLIER = 100; // Multiplier for percentage calculations

// Font size ranges for different size groups
const SIZE_RANGES = {
	large: { min: 100, max: 120 },
	medium: { min: 60, max: 80 },
	small: { min: 20, max: 50 }
};

// ==========================
// GAME STATE
// ==========================

let currentTarget: CurrentTarget | null = null;

let questions: Question[] = [];
let currentQuestionIndex = 0;

let totalQuestions = 0;
let correctAnswers = 0;
let incorrectAnswers = 0;

let sizeGroupStats = {
	large: { total: 0, correct: 0, incorrect: 0, accuracy: 0 },
	medium: { total: 0, correct: 0, incorrect: 0, accuracy: 0 },
	small: { total: 0, correct: 0, incorrect: 0, accuracy: 0 }
};

let responseTimes: number[] = [];

let answerInput = '';

let targetTimer: ReturnType<typeof setTimeout> | null = null;

let testFinished = false;

let testStarted = false;

let testResult: TestResult | null = null;

let loadingRecommendations = false;

let recommendationError = '';

// ==========================
// WEBSOCKET / NATS CONNECTION
// ==========================

// Commented out WebSocket/NATS bridge connection
/*
let ws: WebSocket | null = null;
let visionReady = false;
let faceDetected = false;
let visionDistance: number | null = null;
let wsConnected = false;
let distanceStatus = 'no_face'; // 'no_face', 'no_distance', 'too_near', 'too_far', 'perfect'
let testEndedDueToNoFace = false;
let consecutiveDistanceCount = 0; // Counter for consecutive distance measurements
let displayDistanceStatus = 'no_face'; // The status to display (only updated after 5 consecutive measurements)
*/

// Set default values for commented-out WebSocket state
let visionReady = true;
let wsConnected = false;
let testEndedDueToNoFace = false;
let displayDistanceStatus = 'perfect';
let consecutiveDistanceCount = 0;
let ws: WebSocket | null = null;
let visionDistance: number | null = null;

// ==========================
// LIFECYCLE
// ==========================

import { onMount, onDestroy } from 'svelte';

// Commented out WebSocket connection lifecycle
/*
onMount(() => {
	connectWebSocket();
});

onDestroy(() => {
	disconnectWebSocket();
});
*/

// ==========================
// WEBSOCKET CONNECTION
// ==========================

// Commented out WebSocket connection functions
/*
function connectWebSocket() {
	try {
		ws = new WebSocket(WEBSOCKET_URL);

		ws.onopen = () => {
			console.log('WebSocket connected to bridge');
			wsConnected = true;
		};

		ws.onmessage = (event) => {
			const data = event.data;
			console.log('Received from bridge:', data);

			// Try to parse as JSON first
			try {
				const jsonData = JSON.parse(data);
				console.log('Parsed JSON:', jsonData);
				// Check if this is a depth message with distance data
				if (jsonData.mean !== undefined) {
					visionDistance = Math.round(jsonData.mean * DISTANCE_ROUNDING_FACTOR) / DISTANCE_ROUNDING_FACTOR;
					console.log('Distance updated:', visionDistance, 'from mean:', jsonData.mean);
				}
			} catch (e) {
				console.log('Not JSON, handling as string');
				// Not JSON, handle as string
				// Parse the message from bridge
				if (data === 'true') {
					visionReady = true;
				} else if (data === 'false') {
					visionReady = false;
				} else if (['too_near', 'too_far', 'perfect', 'no_face', 'no_distance'].includes(data)) {
					distanceStatus = data;

					// Handle face detection and no distance immediately (no delay)
					if (data === 'no_face' || data === 'no_distance') {
						console.log('Face or distance not detected - testStarted:', testStarted, 'testEndedDueToNoFace:', testEndedDueToNoFace);
						// Check if face is not detected during test
						if (testStarted && !testEndedDueToNoFace) {
							console.log('Ending test due to no face/distance');
							testEndedDueToNoFace = true;
							testStarted = false;
							// Clear the target timer if running
							if (targetTimer) {
								clearTimeout(targetTimer);
								targetTimer = null;
							}
							// Send face not detected message to backend
							if (ws && wsConnected) {
								try {
									ws.send(JSON.stringify({
										type: 'face_not_detected',
										distance: visionDistance || 0
									}));
								} catch (error) {
									console.error('Failed to send face not detected message:', error);
								}
							}
						}
						displayDistanceStatus = data === 'no_face' ? 'no_face' : 'no_distance';
						consecutiveDistanceCount = 0;
						visionReady = false;
					} else {
						// Handle distance status with consecutive measurement requirement
						if (data === distanceStatus) {
							consecutiveDistanceCount++;
						} else {
							consecutiveDistanceCount = 1;
						}

						// Only update display status after threshold consecutive measurements
						if (consecutiveDistanceCount >= CONSECUTIVE_MEASUREMENTS_THRESHOLD) {
							displayDistanceStatus = data;
						}

						// Update visionReady based on distance status
						visionReady = data === 'perfect';
					}
				}
			}
		};

		ws.onerror = (error) => {
			console.error('WebSocket error:', error);
			wsConnected = false;
		};

		ws.onclose = () => {
			console.log('WebSocket disconnected');
			wsConnected = false;
			// Attempt to reconnect after delay
			setTimeout(connectWebSocket, WEBSOCKET_RECONNECT_DELAY);
		};
	} catch (error) {
		console.error('Failed to connect to WebSocket:', error);
		wsConnected = false;
	}
}

function disconnectWebSocket() {
	if (ws) {
		ws.close();
		ws = null;
	}
	wsConnected = false;
}
*/

// ==========================
// TARGETS
// ==========================

const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
const NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
const WORDS = ['CAT', 'DOG', 'BOOK', 'HOUSE', 'PHONE', 'TREE', 'FISH', 'BIRD', 'STAR', 'MOON'];
const SHAPES = ['○', '□', '△', '☆']; // circle, square, triangle, star
const OBJECTS = [
	{ display: '🍎', answer: 'apple' },
	{ display: '🍌', answer: 'banana' },
	{ display: '🍇', answer: 'grapes' },
	{ display: '🍊', answer: 'orange' },
	{ display: '🐶', answer: 'dog' },
	{ display: '🐱', answer: 'cat' },
	{ display: '🦁', answer: 'lion' },
	{ display: '🐯', answer: 'tiger' },
	{ display: '🐘', answer: 'elephant' },
	{ display: '🦜', answer: 'parrot' },
	{ display: '🦉', answer: 'owl' },
	// { display: '🦅', answer: 'eagle' },
	{ display: '🚗', answer: 'car' },
	{ display: '📱', answer: 'phone' },
	{ display: '📚', answer: 'book' },
	{ display: '⚽', answer: 'ball' },
	{ display: '🕐', answer: 'clock' }
];

const SHAPE_ANSWERS: Record<string, string> = {
	'○': 'circle',
	'□': 'square',
	'△': 'triangle',
	'☆': 'star'
};

// ==========================
// QUESTION GENERATOR
// ==========================

function generateQuestions(): Question[] {
	const questions: Question[] = [];
	const sizeGroups: ('large' | 'medium' | 'small')[] = ['large', 'medium', 'small'];
	const categories: ('letter' | 'number' | 'word' | 'shape' | 'object')[] = ['letter', 'number', 'word', 'shape', 'object'];

	// Generate questions per size group
	for (const sizeGroup of sizeGroups) {
		const sizeGroupQuestions: Question[] = [];
		for (let i = 0; i < QUESTIONS_PER_SIZE_GROUP; i++) {
			const category = categories[Math.floor(Math.random() * categories.length)];
			let display: string;
			let answer: string;

			switch (category) {
				case 'letter':
					display = LETTERS[Math.floor(Math.random() * LETTERS.length)];
					answer = display.toLowerCase();
					break;
				case 'number':
					display = NUMBERS[Math.floor(Math.random() * NUMBERS.length)];
					answer = display;
					break;
				case 'word':
					display = WORDS[Math.floor(Math.random() * WORDS.length)];
					answer = display.toLowerCase();
					break;
				case 'shape':
					display = SHAPES[Math.floor(Math.random() * SHAPES.length)];
					answer = SHAPE_ANSWERS[display];
					break;
				case 'object':
					const obj = OBJECTS[Math.floor(Math.random() * OBJECTS.length)];
					display = obj.display;
					answer = obj.answer;
					break;
			}

			const sizeRange = SIZE_RANGES[sizeGroup];
			const size = Math.floor(Math.random() * (sizeRange.max - sizeRange.min + 1)) + sizeRange.min;

			sizeGroupQuestions.push({
				display,
				answer,
				size,
				sizeGroup,
				category
			});
		}
		// Shuffle within the size group and add to main questions array
		questions.push(...shuffleArray(sizeGroupQuestions));
	}

	// Return questions in order: large, medium, small
	return questions;
}

function shuffleArray<T>(array: T[]): T[] {
	const shuffled = [...array];
	for (let i = shuffled.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
	}
	return shuffled;
}

// ==========================
// START TEST
// ==========================

function startTest() {
	resetTest();

	// Generate balanced questions
	questions = generateQuestions();
	currentQuestionIndex = 0;
	testStarted = true;



	showNextQuestion();
}



// ==========================
// RESET
// ==========================

function resetTest() {
	questions = [];
	currentQuestionIndex = 0;

	totalQuestions = 0;
	correctAnswers = 0;
	incorrectAnswers = 0;

	sizeGroupStats = {
		large: { total: 0, correct: 0, incorrect: 0, accuracy: 0 },
		medium: { total: 0, correct: 0, incorrect: 0, accuracy: 0 },
		small: { total: 0, correct: 0, incorrect: 0, accuracy: 0 }
	};

	responseTimes = [];

	testFinished = false;
	testStarted = false;

	testResult = null;

	answerInput = '';

	testEndedDueToNoFace = false;

	// consecutiveDistanceCount = 0; // Commented out - not used without WebSocket
	// displayDistanceStatus = 'no_face'; // Commented out - not used without WebSocket

	currentTarget = null;
}

// ==========================
// SHOW NEXT QUESTION
// ==========================

function showNextQuestion() {
	if (currentQuestionIndex >= questions.length) {
		finishTest();
		return;
	}

	const question = questions[currentQuestionIndex];

	currentTarget = {
		display: question.display,
		answer: question.answer,
		size: question.size,
		sizeGroup: question.sizeGroup,
		shownAt: Date.now()
	};

	// Clear existing timer if any
	if (targetTimer) {
		clearTimeout(targetTimer);
	}

	// Set timer for automatic progression
	targetTimer = setTimeout(() => {
		if (currentTarget && !testFinished) {
			// Count as incorrect if not answered
			processAnswer('', true);
		}
	}, QUESTION_TIMER_DURATION);
}

// ==========================
// ANSWER PROCESSING
// ==========================

function processAnswer(input: string, timeout: boolean = false) {
	if (!currentTarget) return;

	// Clear the target timer
	if (targetTimer) {
		clearTimeout(targetTimer);
		targetTimer = null;
	}

	totalQuestions++;

	const responseTime = timeout ? QUESTION_TIMER_DURATION : Date.now() - currentTarget.shownAt;
	responseTimes.push(responseTime);

	const trimmedInput = input.trim();
	const correct = timeout ? false : trimmedInput.includes(currentTarget.answer);
	console.log('Answer check:', { input, trimmedInput, answer: currentTarget.answer, correct });

	// Update size group stats
	const sizeGroup = currentTarget.sizeGroup;
	sizeGroupStats[sizeGroup].total++;

	if (correct) {
		correctAnswers++;
		sizeGroupStats[sizeGroup].correct++;
	} else {
		incorrectAnswers++;
		sizeGroupStats[sizeGroup].incorrect++;
	}

	// Calculate accuracy for this size group
	sizeGroupStats[sizeGroup].accuracy = Math.round(
		(sizeGroupStats[sizeGroup].correct / sizeGroupStats[sizeGroup].total) * PERCENTAGE_MULTIPLIER
	);

	// Send item recognition data to backend - commented out
	/*
	if (ws && wsConnected) {
		try {
			ws.send(JSON.stringify({
				type: 'item_recognized',
				display: currentTarget.display,
				answer: currentTarget.answer,
				userAnswer: input,
				size: currentTarget.size,
				sizeGroup: currentTarget.sizeGroup,
				category: questions[currentQuestionIndex]?.category || 'unknown',
				distance: visionDistance || 0,
				correct: correct,
				responseTime: responseTime
			}));
		} catch (error) {
			console.error('Failed to send item recognition data:', error);
		}
	}
	*/

	answerInput = '';

	currentQuestionIndex++;
	showNextQuestion();
}

// ==========================
// ACCURACY
// ==========================

function getOverallAccuracy(): number {
	if (totalQuestions === 0) {
		return 0;
	}
	return Math.round((correctAnswers / totalQuestions) * PERCENTAGE_MULTIPLIER);
}

function getAverageResponseTime(): number {
	if (responseTimes.length === 0) {
		return 0;
	}
	return Math.round(responseTimes.reduce((a: number, b: number) => a + b, 0) / responseTimes.length);
}

// ==========================
// INFERENCE LOGIC
// ==========================

function getVisionCategory(): string {
	const largeAccuracy = sizeGroupStats.large.accuracy;
	const mediumAccuracy = sizeGroupStats.medium.accuracy;
	const smallAccuracy = sizeGroupStats.small.accuracy;
	const overallAccuracy = getOverallAccuracy();
	const largeErrors = sizeGroupStats.large.incorrect;
	const mediumErrors = sizeGroupStats.medium.incorrect;
	const smallErrors = sizeGroupStats.small.incorrect;

	// AI-based inference logic with weighted scoring
	let hyperopiaScore = 0;
	let myopiaScore = 0;
	let generalWeaknessScore = 0;
	let normalVisionScore = 0;

	// Large target issues suggest hyperopia (farsightedness)
	if (largeAccuracy < ACCURACY_THRESHOLD_LOW) hyperopiaScore += SCORE_HIGH_ISSUE;
	if (largeErrors >= ERROR_COUNT_HIGH) hyperopiaScore += SCORE_MODERATE_ISSUE;
	if (largeAccuracy < mediumAccuracy) hyperopiaScore += SCORE_MINOR_ISSUE;

	// Small target issues suggest myopia (nearsightedness)
	if (smallAccuracy < ACCURACY_THRESHOLD_LOW) myopiaScore += SCORE_HIGH_ISSUE;
	if (smallErrors >= ERROR_COUNT_HIGH) myopiaScore += SCORE_MODERATE_ISSUE;
	if (smallAccuracy < mediumAccuracy) myopiaScore += SCORE_MINOR_ISSUE;

	// Medium target issues suggest general weakness
	if (mediumAccuracy < ACCURACY_THRESHOLD_LOW) generalWeaknessScore += SCORE_MODERATE_ISSUE;
	if (mediumErrors >= ERROR_COUNT_HIGH) generalWeaknessScore += SCORE_MODERATE_ISSUE;

	// Normal vision indicators
	if (overallAccuracy >= ACCURACY_THRESHOLD_OVERALL) normalVisionScore += SCORE_NORMAL_HIGH;
	if (largeAccuracy >= ACCURACY_THRESHOLD_HIGH && mediumAccuracy >= ACCURACY_THRESHOLD_HIGH && smallAccuracy >= ACCURACY_THRESHOLD_LOW) normalVisionScore += SCORE_NORMAL_MEDIUM;
	if (largeErrors <= ERROR_COUNT_LOW_LARGE && mediumErrors <= ERROR_COUNT_LOW_MEDIUM && smallErrors <= ERROR_COUNT_LOW_SMALL) normalVisionScore += SCORE_NORMAL_LOW;

	// Determine highest score
	const scores = {
		'Possible Hyperopia (Farsightedness)': hyperopiaScore,
		'Possible Myopia (Nearsightedness)': myopiaScore,
		'General Vision Weakness': generalWeaknessScore,
		'Normal Vision': normalVisionScore
	};

	const maxScore = Math.max(...Object.values(scores));
	const visionCategory = Object.keys(scores).find(key => scores[key as keyof typeof scores] === maxScore);

	// Combined vision issues analysis
	const combinedConditions: string[] = [];
	if (hyperopiaScore >= COMBINED_VISION_CUTOFF) combinedConditions.push('Hyperopia');
	if (myopiaScore >= COMBINED_VISION_CUTOFF) combinedConditions.push('Myopia');
	if (generalWeaknessScore >= COMBINED_VISION_CUTOFF) combinedConditions.push('General Vision Weakness');

	// If multiple conditions are above cutoff, provide combined analysis
	if (combinedConditions.length >= 2) {
		return `Possible Combined Vision Issues (${combinedConditions.join(' + ')})`;
	}

	return visionCategory || 'Vision Impairment Detected';
}

async function generateRecommendations(): Promise<string[]> {
	loadingRecommendations = true;
	recommendationError = '';

	try {
		const response = await fetch('http://localhost:5000/api/ai/vision-recommendations', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				overallAccuracy: getOverallAccuracy(),
				largeAccuracy: sizeGroupStats.large.accuracy,
				mediumAccuracy: sizeGroupStats.medium.accuracy,
				smallAccuracy: sizeGroupStats.small.accuracy,
				largeCorrect: sizeGroupStats.large.correct,
				largeIncorrect: sizeGroupStats.large.incorrect,
				mediumCorrect: sizeGroupStats.medium.correct,
				mediumIncorrect: sizeGroupStats.medium.incorrect,
				smallCorrect: sizeGroupStats.small.correct,
				smallIncorrect: sizeGroupStats.small.incorrect,
				averageResponseTime: getAverageResponseTime()
			})
		});

		const data = await response.json();

		if (data.success) {
			loadingRecommendations = false;
			return data.data.recommendations;
		} else {
			loadingRecommendations = false;
			recommendationError = data.error || 'Failed to generate AI recommendations';
			return getFallbackRecommendations();
		}
	} catch (error) {
		loadingRecommendations = false;
		recommendationError = 'Failed to connect to AI service';
		return getFallbackRecommendations();
	}
}

function getFallbackRecommendations(): string[] {
	const recommendations: string[] = [];
	const largeAccuracy = sizeGroupStats.large.accuracy;
	const mediumAccuracy = sizeGroupStats.medium.accuracy;
	const smallAccuracy = sizeGroupStats.small.accuracy;
	const overallAccuracy = getOverallAccuracy();

	if (largeAccuracy < RECOMMENDATION_THRESHOLD_LOW) {
		recommendations.push('Difficulty with large targets detected - possible distance vision issue. Consider consulting an eye specialist.');
	}

	if (smallAccuracy < RECOMMENDATION_THRESHOLD_LOW) {
		recommendations.push('Difficulty with small-size recognition detected - possible near vision weakness. May indicate myopia or need for reading glasses.');
	}

	if (mediumAccuracy < RECOMMENDATION_THRESHOLD_LOW) {
		recommendations.push('Consistent errors in normal vision range detected - general visual clarity issue recommended for evaluation.');
	}

	if (overallAccuracy >= RECOMMENDATION_THRESHOLD_EXCELLENT) {
		recommendations.push('Excellent overall vision performance. Continue with regular eye check-ups.');
	}

	if (recommendations.length === 0) {
		recommendations.push('Your vision performance shows mixed results. A comprehensive eye examination is recommended.');
	}

	return recommendations;
}

// ==========================
// FINISH TEST
// ==========================

async function finishTest() {
	testFinished = true;

	// Clear the target timer
	if (targetTimer) {
		clearTimeout(targetTimer);
		targetTimer = null;
	}

	// Generate test result with AI recommendations
	const aiRecommendations = await generateRecommendations();

	testResult = {
		totalQuestions,
		correctAnswers,
		incorrectAnswers,
		overallAccuracy: getOverallAccuracy(),
		large: { ...sizeGroupStats.large },
		medium: { ...sizeGroupStats.medium },
		small: { ...sizeGroupStats.small },
		averageResponseTime: getAverageResponseTime(),
		visionCategory: getVisionCategory(),
		recommendations: aiRecommendations
	};
}

// ==========================
// REPORT
// ==========================

$: currentProgress = currentQuestionIndex + 1;
</script>

<div class="game-container">
	{#if !testFinished}
		<!-- Intro Screen -->
		{#if !testStarted}
			<div class="intro-screen">
				{#if testEndedDueToNoFace}
					<h1 class="title">Test Ended</h1>
					<p class="description">
						Face is not detected so exited from game. Please ensure your face is in front of the camera and try again.
					</p>
					<button
						class="start-button"
						on:click={() => {
							testEndedDueToNoFace = false;
						}}
					>
						Try Again
					</button>
				{:else}
					<h1 class="title">Visual Acuity Test</h1>
					<p class="description">
						15 questions testing your vision across different sizes. Each question appears for 5 seconds.
					</p>

					<!-- Vision Status -->
					<div class="vision-status">
						<div class="status-item">
							<span class="status-label">Connection:</span>
							<span class="status-value {wsConnected ? 'connected' : 'disconnected'}">
								{wsConnected ? 'Connected' : 'Disconnected'}
							</span>
						</div>
						<div class="status-item">
							<span class="status-label">Vision System:</span>
							<span class="status-value {visionReady ? 'ready' : 'not-ready'}">
								{visionReady ? 'Ready' : 'Not Ready'}
							</span>
						</div>
					</div>

					<!-- Distance Warning -->
					{#if displayDistanceStatus === 'too_near'}
						<div class="distance-warning warning-near">
							⚠️ You are too near the camera. Move back to approximately 130cm from the screen.
						</div>
					{:else if displayDistanceStatus === 'too_far'}
						<div class="distance-warning warning-far">
							⚠️ You are too far from the camera. Move closer to approximately 130cm from the screen.
						</div>
					{:else if displayDistanceStatus === 'no_face'}
						<div class="distance-warning warning-no-face">
							⚠️ No face detected. Please position yourself in front of the camera.
						</div>
					{:else if displayDistanceStatus === 'perfect'}
						<div class="distance-warning warning-perfect">
							✅ Perfect distance! You are at the optimal position (130cm).
						</div>
					{/if}

					<button
						class="start-button"
						on:click={startTest}
						disabled={!visionReady}
						class:disabled={!visionReady}
					>
						{visionReady ? 'Start Test' : 'Waiting for Vision System...'}
					</button>
				{/if}
			</div>
		{:else}
			<!-- Game Screen -->
			<div class="game-screen">
				<div class="progress">Question {currentProgress} / 15</div>

				<!-- Distance Warning During Test -->
				{#if displayDistanceStatus === 'too_near'}
					<div class="game-distance-warning warning-near">
						⚠️ Too near! Move back to 130cm
					</div>
				{:else if displayDistanceStatus === 'too_far'}
					<div class="game-distance-warning warning-far">
						⚠️ Too far! Move closer to 130cm
					</div>
				{:else if displayDistanceStatus === 'no_face'}
					<div class="game-distance-warning warning-no-face">
						⚠️ No face detected
					</div>
				{/if}

				{#if currentTarget}
					<div class="target-display" style="font-size: {currentTarget.size}px">
						{currentTarget.display}
					</div>
				{/if}

				<input
					type="text"
					bind:value={answerInput}
					on:keydown={(e) => {
						if (e.key === 'Enter') {
							processAnswer(answerInput);
						}
					}}
					placeholder="Type what you see and press Enter"
					class="answer-input"
				/>
			</div>
		{/if}
	{:else}
		<!-- Results Screen -->
		{#if testResult}
			<div class="results-screen">
				<h2 class="results-title">Test Complete</h2>
				
				<div class="score-circle">
					<span class="score-value">{testResult.correctAnswers}/15</span>
					<span class="score-label">Total Score</span>
				</div>
				
				<div class="accuracy-display">
					<span class="accuracy-value">{testResult.overallAccuracy}%</span>
					<span class="accuracy-label">Overall Accuracy</span>
				</div>
				
				<div class="rating-box">
					<span class="rating-label">AI Vision Analysis</span>
					<span class="rating-value">{testResult.visionCategory}</span>
				</div>
				
				<div class="size-group-breakdown">
					<h3 class="breakdown-title">Detailed Size Group Analysis</h3>
					<div class="size-group-grid">
						<div class="size-group-item">
							<span class="size-group-label">Large (100-120px)</span>
							<span class="size-group-accuracy">{testResult.large.accuracy}%</span>
							<span class="size-group-detail">Answered: {testResult.large.correct}/8</span>
							<span class="size-group-detail">Missed: {testResult.large.incorrect}/8</span>
						</div>
						<div class="size-group-item">
							<span class="size-group-label">Medium (60-80px)</span>
							<span class="size-group-accuracy">{testResult.medium.accuracy}%</span>
							<span class="size-group-detail">Answered: {testResult.medium.correct}/8</span>
							<span class="size-group-detail">Missed: {testResult.medium.incorrect}/8</span>
						</div>
						<div class="size-group-item">
							<span class="size-group-label">Small (20-50px)</span>
							<span class="size-group-accuracy">{testResult.small.accuracy}%</span>
							<span class="size-group-detail">Answered: {testResult.small.correct}/8</span>
							<span class="size-group-detail">Missed: {testResult.small.incorrect}/8</span>
						</div>
					</div>
				</div>
				
				
				<!-- <div class="recommendation-box">
					<span class="recommendation-label">AI Recommendations</span>
					{#if loadingRecommendations}
						<p class="recommendation-text">Generating AI-powered recommendations...</p>
					{:else if recommendationError}
						<p class="recommendation-text error">{recommendationError}</p>
						<p class="recommendation-text">Showing fallback recommendations:</p>
						{#each testResult.recommendations as rec}
							<p class="recommendation-text">{rec}</p>
						{/each}
					{:else}
						{#each testResult.recommendations as rec}
							<p class="recommendation-text">{rec}</p>
						{/each}
					{/if}
				</div> -->
				
				<div class="button-group">
					<button class="restart-button" on:click={resetTest}>
						🔄 Retake Test
					</button>
					<a href="/" class="home-button">🏠 Back to Home</a>
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.game-container {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.intro-screen {
		text-align: center;
		padding: 40px;
	}

	.title {
		font-size: 48px;
		font-weight: 800;
		margin-bottom: 20px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.description {
		font-size: 20px;
		color: #666;
		margin-bottom: 40px;
		line-height: 1.6;
	}

	.vision-status {
		background: #f9fafb;
		border-radius: 12px;
		padding: 20px;
		margin-bottom: 30px;
		width: 100%;
		max-width: 400px;
	}

	.status-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 8px 0;
		border-bottom: 1px solid #e5e7eb;
	}

	.status-item:last-child {
		border-bottom: none;
	}

	.status-label {
		font-size: 14px;
		color: #666;
		font-weight: 600;
	}

	.status-value {
		font-size: 14px;
		font-weight: 700;
	}

	.status-value.connected {
		color: #10b981;
	}

	.status-value.disconnected {
		color: #ef4444;
	}

	.status-value.ready {
		color: #10b981;
	}

	.status-value.not-ready {
		color: #f59e0b;
	}

	.distance-warning {
		background: #fff3cd;
		border: 2px solid #ffc107;
		border-radius: 8px;
		padding: 12px 16px;
		margin-bottom: 20px;
		font-size: 14px;
		text-align: center;
		font-weight: 600;
	}

	.distance-warning.warning-near {
		background: #fee2e2;
		border-color: #ef4444;
		color: #dc2626;
	}

	.distance-warning.warning-far {
		background: #fee2e2;
		border-color: #ef4444;
		color: #dc2626;
	}

	.distance-warning.warning-no-face {
		background: #fef3c7;
		border-color: #f59e0b;
		color: #d97706;
	}

	.distance-warning.warning-perfect {
		background: #d1fae5;
		border-color: #10b981;
		color: #059669;
	}

	.game-distance-warning {
		background: rgba(255, 255, 255, 0.95);
		border: 2px solid #ffc107;
		border-radius: 8px;
		padding: 8px 12px;
		margin-bottom: 10px;
		font-size: 12px;
		text-align: center;
		font-weight: 600;
		animation: pulse 2s infinite;
	}

	.game-distance-warning.warning-near {
		background: rgba(254, 226, 226, 0.95);
		border-color: #ef4444;
		color: #dc2626;
	}

	.game-distance-warning.warning-far {
		background: rgba(254, 226, 226, 0.95);
		border-color: #ef4444;
		color: #dc2626;
	}

	.game-distance-warning.warning-no-face {
		background: rgba(254, 243, 199, 0.95);
		border-color: #f59e0b;
		color: #d97706;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.7;
		}
	}

	.start-button {
		padding: 16px 48px;
		font-size: 18px;
		font-weight: 700;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 12px;
		cursor: pointer;
		transition: transform 0.2s;
	}

	.start-button:hover {
		transform: scale(1.05);
	}

	.start-button.disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	.start-button.disabled:hover {
		transform: none;
	}

	.game-screen {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 40px;
		padding: 40px;
	}

	.progress {
		font-size: 24px;
		font-weight: 700;
		color: #666;
	}

	.target-display {
		font-weight: 800;
		text-align: center;
		transition: font-size 0.3s ease;
	}

	.answer-input {
		padding: 16px 24px;
		font-size: 18px;
		background-color: #f4f0f0;
		border: 2px solid #ddd;
		border-radius: 12px;
		width: 300px;
		text-align: center;
	}

	.answer-input:focus {
		outline: none;
		border-color: #667eea;
	}

	.results-screen {
		text-align: center;
		padding: 40px;
		max-width: 600px;
	}

	.results-title {
		font-size: 36px;
		font-weight: 800;
		margin-bottom: 30px;
	}

	.score-circle {
		width: 150px;
		height: 150px;
		border-radius: 50%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		margin: 0 auto 20px;
	}

	.score-value {
		font-size: 48px;
		font-weight: 800;
		color: white;
	}

	.score-label {
		font-size: 14px;
		color: rgba(255, 255, 255, 0.9);
	}

	.accuracy-display {
		text-align: center;
		margin-bottom: 30px;
	}

	.accuracy-value {
		font-size: 36px;
		font-weight: 800;
		color: #667eea;
	}

	.accuracy-label {
		font-size: 14px;
		color: #666;
	}

	.rating-box {
		background: #f5f5f5;
		border-radius: 12px;
		padding: 20px;
		margin-bottom: 30px;
	}

	.rating-label {
		display: block;
		font-size: 14px;
		color: #666;
		margin-bottom: 8px;
	}

	.rating-value {
		font-size: 28px;
		font-weight: 800;
		color: #333;
	}

	.size-group-breakdown {
		background: #f9fafb;
		border-radius: 12px;
		padding: 24px;
		margin-bottom: 30px;
	}

	.breakdown-title {
		font-size: 18px;
		font-weight: 700;
		color: #333;
		margin-bottom: 16px;
	}

	.size-group-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
	}

	.size-group-item {
		background: white;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 16px;
		text-align: center;
	}

	.size-group-label {
		display: block;
		font-size: 12px;
		color: #666;
		margin-bottom: 8px;
	}

	.size-group-accuracy {
		display: block;
		font-size: 24px;
		font-weight: 800;
		color: #667eea;
		margin-bottom: 4px;
	}

	.size-group-detail {
		display: block;
		font-size: 12px;
		color: #999;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
		margin-bottom: 30px;
	}

	.stat-item {
		background: white;
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 16px;
	}

	.stat-label {
		display: block;
		font-size: 12px;
		color: #666;
		margin-bottom: 8px;
	}

	.stat-value {
		display: block;
		font-size: 24px;
		font-weight: 800;
		color: #333;
	}

	.stat-value.correct {
		color: #10b981;
	}

	.stat-value.incorrect {
		color: #ef4444;
	}

	.recommendation-box {
		background: #f0f9ff;
		border: 1px solid #667eea;
		border-radius: 12px;
		padding: 20px;
		margin-bottom: 30px;
	}

	.recommendation-label {
		display: block;
		font-size: 14px;
		font-weight: 700;
		color: #667eea;
		margin-bottom: 8px;
	}

	.recommendation-text {
		font-size: 16px;
		color: #333;
		line-height: 1.6;
		margin: 0;
	}

	.recommendation-text.error {
		color: #ef4444;
		font-weight: 600;
	}

	.restart-button {
		padding: 16px 48px;
		font-size: 18px;
		font-weight: 700;
		background: #333;
		color: white;
		border: none;
		border-radius: 12px;
		cursor: pointer;
		transition: background 0.2s;
	}

	.restart-button:hover {
		background: #555;
	}

	.button-group {
		display: flex;
		gap: 12px;
		justify-content: center;
		align-items: center;
	}

	.home-button {
		padding: 16px 48px;
		font-size: 18px;
		font-weight: 700;
		background: #6b7280;
		color: white;
		text-decoration: none;
		border: none;
		border-radius: 12px;
		cursor: pointer;
		transition: background 0.2s;
		display: inline-block;
	}

	.home-button:hover {
		background: #4b5563;
	}
</style>