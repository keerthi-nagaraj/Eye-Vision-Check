<script lang="ts">
	import TritanPlate from '$lib/components/TritanPlate.svelte';
	import { onMount, onDestroy } from 'svelte';

	const TOTAL_ROUNDS = 6;

	const shapes = ["butterfly", "cat", "fish", "triangle", "circle", "square", "star"];

	// Configurable constants
	const WEBSOCKET_URL = 'ws://localhost:8765';
	const DISTANCE_ROUNDING_FACTOR = 10;

	let round = 0;
	let currentShape = "";
	let answer = "";
	let completed = false;
	let showAnswer = false;

	let shuffledShapes: string[] = [];
	let shapeIndex = 0;

	let results: any[] = [];

	// Vision status variables
	// Commented out WebSocket/NATS bridge connection
	/*
	let ws: WebSocket | null = null;
	let visionReady = false;
	let distanceStatus = 'no_face'; // 'no_face', 'no_distance', 'too_near', 'too_far', 'perfect'
	let visionDistance: number | null = null;
	let wsConnected = false;
	let testStarted = false;
	let testEndedDueToNoFace = false;
	let consecutiveDistanceCount = 0;
	let displayDistanceStatus = 'no_face';
	*/

	// Set default values for commented-out WebSocket state
	let visionReady = true;
	let wsConnected = false;
	let testStarted = false;
	let testEndedDueToNoFace = false;
	let displayDistanceStatus = 'perfect';
	let consecutiveDistanceCount = 0;
	let ws: WebSocket | null = null;
	let visionDistance: number | null = null;

	// ==========================
	// LIFECYCLE
	// ==========================

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
							// Handle distance status with 5 consecutive measurement requirement
							if (data === distanceStatus) {
								consecutiveDistanceCount++;
							} else {
								consecutiveDistanceCount = 1;
							}

							
							// Only update display status after 5 consecutive measurements
							if (consecutiveDistanceCount >= 5) {
								displayDistanceStatus = data;
							}

							// Update visionReady based on distance status
							visionReady = data === 'perfect';
						}
					}
				}
			};

			ws.onclose = () => {
				console.log('WebSocket disconnected');
				wsConnected = false;
				visionReady = false;
			};

			ws.onerror = (error) => {
				console.error('WebSocket error:', error);
				wsConnected = false;
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

	function startTest() {
		if (visionReady) {
			testStarted = true;
		}
	}

	function shuffleArray<T>(array: T[]): T[] {
		const shuffled = [...array];
		for (let i = shuffled.length - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
		}
		return shuffled;
	}

	function newRound() {
		if (shapeIndex >= shuffledShapes.length) {
			// Reshuffle if we've used all shapes
			shuffledShapes = shuffleArray(shapes);
			shapeIndex = 0;
		}
		currentShape = shuffledShapes[shapeIndex];
		shapeIndex++;
		showAnswer = false;
		answer = "";
	}

	onMount(() => newRound());

	function handleKey(e: KeyboardEvent) {
		if (e.key !== "Enter") return;
		if (!answer.trim()) return;

		const correct =
			answer.toLowerCase().includes(currentShape.toLowerCase());

		// Send answer data to backend via WebSocket - commented out
		/*
		if (ws && wsConnected) {
			try {
				ws.send(JSON.stringify({
					type: 'tritan_answer',
					round: round + 1,
					targetShape: currentShape,
					userAnswer: answer,
					correct: correct,
					distance: visionDistance || 0
				}));
			} catch (error) {
				console.error('Failed to send Tritan answer data:', error);
			}
		}
		*/

		results = [
			...results,
			{
				round,
				target: currentShape,
				response: answer,
				correct
			}
		];

		round++;

		if (round >= TOTAL_ROUNDS) {
			completed = true;
			// Send completion data to backend
			sendTritanCompletion();
		} else {
			newRound();
		}
	}

	function sendTritanCompletion() {
		const score = calculateScore();
		const diagnosis = getDiagnosis();

		// Send completion data to backend - commented out
		/*
		if (ws && wsConnected) {
			try {
				ws.send(JSON.stringify({
					type: 'tritan_complete',
					totalRounds: TOTAL_ROUNDS,
					correct: results.filter(r => r.correct).length,
					score: score,
					diagnosis: diagnosis,
					distance: visionDistance || 0
				}));
			} catch (error) {
				console.error('Failed to send Tritan completion data:', error);
			}
		}
		*/
	}

	function calculateScore() {
		const correct = results.filter((r) => r.correct).length;
		return Math.round((correct / results.length) * 100);
	}

	function getDiagnosis() {
		const score = calculateScore();
		if (score >= 80) {
			return 'Normal Tritan Vision';
		}
		if (score >= 50) {
			return 'Mild Tritan Deficiency';
		}
		return 'Strong Tritan Deficiency';
	}

	function resetTest() {
		testStarted = false;
		testEndedDueToNoFace = false;
		// consecutiveDistanceCount = 0; // Commented out - not used without WebSocket
		// displayDistanceStatus = 'no_face'; // Commented out - not used without WebSocket
		round = 0;
		currentShape = "";
		answer = "";
		completed = false;
		showAnswer = false;
		results = [];
		shuffledShapes = shuffleArray(shapes);
		shapeIndex = 0;
		newRound();
	}
</script>

<div class="container">
	{#if !testStarted && !testEndedDueToNoFace}
		<!-- Intro Screen -->
		<h1>Tritan Color Vision Test</h1>
		<p class="subtitle">Color vision test with tritan plates</p>

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
			on:click={startTest}
			disabled={!visionReady}
			class="start-button {visionReady ? 'enabled' : 'disabled'}"
		>
			{visionReady ? 'Start Test' : 'Waiting for Vision Ready...'}
		</button>

	{:else if testEndedDueToNoFace}
		<!-- Test Ended Screen -->
		<h1>Test Ended</h1>
		<p class="subtitle">Face or distance was not detected during the test.</p>
		<button
			on:click={() => {
				testEndedDueToNoFace = false;
			}}
			class="start-button enabled"
		>
			Try Again
		</button>

	{:else if !completed}
		<!-- Active Test Screen -->
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

		<h2>Round {round + 1} / {TOTAL_ROUNDS}</h2>

		<TritanPlate
			shape={currentShape}
			showAnswer={showAnswer}
		/>

		<input
			class="input" style="background-color: white; border: 2px solid black;"
			bind:value={answer}
			placeholder="Type shape and press Enter"
			on:keydown={handleKey}
		/>
	{:else}
		<h1>🎉 Tritan Test Results</h1>

		<div class="results-container">
			<div class="score-display">
				<p class="score">{calculateScore()}%</p>
				<p class="result-text">{getDiagnosis()}</p>
				<p class="correct-count">
					{results.filter((r) => r.correct).length} / {results.length} Correct
				</p>
			</div>

			<div class="answers-summary">
				{#each results as result, i}
					<div class="answer-item {result.correct ? 'correct' : 'incorrect'}">
						<div class="answer-info">
							<span class="round">Round {i + 1}</span>
							<span class="target">Target: {result.target}</span>
							<span class="user-ans">Your answer: {result.response}</span>
						</div>
						<div class="answer-status">
							{#if result.correct}
								<span class="status correct">✓</span>
							{:else}
								<span class="status incorrect">✗</span>
							{/if}
						</div>
					</div>
				{/each}
			</div>

			<button class="retake-button" on:click={resetTest}>🔄 Retake Test</button>
		</div>
	{/if}
</div>

<style>
	.container {
		text-align: center;
		font-family: sans-serif;
		padding: 20px;
	}

	h1 {
		font-size: 2rem;
		font-weight: 700;
		color: #333;
	}

	.subtitle {
		font-size: 1rem;
		color: #666;
	}

	.vision-status {
		display: flex;
		flex-direction: column;
		gap: 8px;
		background: white;
		padding: 16px;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.status-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.status-label {
		font-size: 14px;
		font-weight: 600;
		color: #374151;
	}

	.status-value {
		font-size: 14px;
		font-weight: 600;
		padding: 4px 12px;
		border-radius: 8px;
	}

	.status-value.connected {
		background: #d1fae5;
		color: #059669;
	}

	.status-value.disconnected {
		background: #fee2e2;
		color: #dc2626;
	}

	.status-value.ready {
		background: #d1fae5;
		color: #059669;
	}

	.status-value.not-ready {
		background: #fee2e2;
		color: #dc2626;
	}

	.distance-warning {
		background: #fff3cd;
		border: 2px solid #ffc107;
		border-radius: 8px;
		padding: 12px 16px;
		font-size: 14px;
		font-weight: 600;
		text-align: center;
		margin-bottom: 16px;
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
		font-size: 12px;
		font-weight: 600;
		text-align: center;
		margin-bottom: 12px;
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
		padding: 12px 24px;
		border-radius: 8px;
		font-size: 16px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
		border: none;
	}

	.start-button.enabled {
		background: #3b82f6;
		color: white;
	}

	.start-button.enabled:hover {
		background: #2563eb;
	}

	.start-button.disabled {
		background: #9ca3af;
		color: white;
		cursor: not-allowed;
	}


	.input {
		width: 420px;
		padding: 12px;
		margin-top: 10px;
	}

	.results-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 20px;
		width: 100%;
		max-width: 500px;
		margin: 0 auto;
	}

	.score-display {
		text-align: center;
		background: white;
		padding: 20px;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.score {
		font-size: 3rem;
		font-weight: 700;
		color: #3b82f6;
		margin: 10px 0;
	}

	.result-text {
		font-size: 1.2rem;
		color: #666;
		margin: 5px 0;
	}

	.correct-count {
		font-size: 1rem;
		color: #666;
	}

	.answers-summary {
		display: flex;
		flex-direction: column;
		gap: 10px;
		width: 100%;
	}

	.answer-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px;
		background: white;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.answer-item.correct {
		background: #ecfdf5;
	}

	.answer-item.incorrect {
		background: #fef2f2;
	}

	.answer-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
		text-align: left;
	}

	.round {
		font-weight: 600;
		color: #333;
	}

	.target {
		color: #666;
		font-size: 0.9rem;
	}

	.user-ans {
		color: #333;
		font-size: 0.9rem;
	}

	.answer-status {
		display: flex;
		align-items: center;
	}

	.status {
		font-size: 1.5rem;
		font-weight: 700;
	}

	.status.correct {
		color: #10b981;
	}

	.status.incorrect {
		color: #ef4444;
	}

	.retake-button {
		padding: 12px 24px;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 16px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}

	.retake-button:hover {
		background: #2563eb;
	}
</style>