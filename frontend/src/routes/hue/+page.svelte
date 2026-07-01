<script lang="ts">
	import { fly } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';

	interface ColorCap {
		id: number;
		hex: string;
		hue: number;
	}

	interface StoredResult {
		testType: string;
		score: number;
		result: string;
		timestamp: string;
	}

	let submitted = false;

	let accuracy = 0;

	let tes = 0;

	// Configurable thresholds
	const ACCURACY_THRESHOLD_NORMAL = 80; // Threshold for normal color vision
	const ACCURACY_THRESHOLD_MILD = 60; // Threshold for mild color discrimination difficulty
	const MAX_ERROR_MULTIPLIER = 5; // Multiplier for maximum error calculation
	const WEBSOCKET_URL = 'ws://localhost:8765';

	let diagnosis = '';

	let correctOrder: ColorCap[] = [];

	let currentOrder: ColorCap[] = [];

	let selectedOrder: ColorCap[] = [];

	let availableCaps: ColorCap[] = [];

	let inputNumber = '';

	let validationMessage = '';

	let startAnchor: ColorCap | null = null;

	let endAnchor: ColorCap | null = null;

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
						visionDistance = Math.round(jsonData.mean * 10) / 10; // Round to 1 decimal place
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

	// Generate Smooth Spectrum

	function generateSpectrum(
		count: number
	): ColorCap[] {
		const colors: ColorCap[] = [];

		for (let i = 0; i < count; i++) {
			const hue = (360 / count) * i;

			colors.push({
				id: i + 1,
				hue,
				hex: `hsl(${hue}, 90%, 55%)`
			});
		}

		return colors;
	}

	// Shuffle Array

	function shuffle(array: ColorCap[]) {
		for (
			let i = array.length - 1;
			i > 0;
			i--
		) {
			const j = Math.floor(
				Math.random() * (i + 1)
			);

			[array[i], array[j]] = [
				array[j],
				array[i]
			];
		}
	}

	// Initialize Test

	function initializeTest() {
		const fullSpectrum =
			generateSpectrum(6);

		const startIndex = Math.floor(
			Math.random() *
				fullSpectrum.length
		);

		const rotated = [
			...fullSpectrum.slice(
				startIndex
			),
			...fullSpectrum.slice(
				0,
				startIndex
			)
		];

		correctOrder = [...rotated];

		startAnchor = rotated[0];

		endAnchor =
			rotated[rotated.length - 1];

		const middle = [
			...rotated.slice(1, -1)
		];

		shuffle(middle);

		currentOrder = [
			startAnchor,
			...middle,
			endAnchor
		];

		// Start with empty selected order - user must select all caps
		selectedOrder = [];

		// All caps are available initially
		availableCaps = [...currentOrder];

		inputNumber = '';

		validationMessage = '';

		submitted = false;

		accuracy = 0;

		tes = 0;

		diagnosis = '';
	}

	initializeTest();

	// Add Cap by Number (keyboard/voice compatible)
	function addCapByNumber() {
		const num = parseInt(inputNumber.trim());

		validationMessage = '';

		// Validate input
		if (isNaN(num)) {
			validationMessage = 'Please enter a valid number';
			return;
		}

		// Check if cap exists in available caps
		const capIndex = availableCaps.findIndex(c => c.id === num);

		if (capIndex === -1) {
			validationMessage = `Cap ${num} is not available`;
			return;
		}

		// Check if already selected
		if (selectedOrder.some(c => c.id === num)) {
			validationMessage = `Cap ${num} is already selected`;
			return;
		}

		// Add to selected order
		const cap = availableCaps[capIndex];
		selectedOrder = [...selectedOrder, cap];

		// Remove from available
		availableCaps = availableCaps.filter(c => c.id !== num);

		// Clear input
		inputNumber = '';

		// Auto-submit when all caps selected
		if (selectedOrder.length === correctOrder.length) {
			currentOrder = [...selectedOrder];
			submitArrangement();
		}
	}

	// Add cap by clicking on it
	function addCapByClick(capId: number) {
		const cap = availableCaps.find(c => c.id === capId);
		if (!cap) return;

		// Check if already selected
		if (selectedOrder.some(c => c.id === capId)) {
			validationMessage = `Cap ${capId} is already selected`;
			return;
		}

		validationMessage = '';

		// Add to selected order
		selectedOrder = [...selectedOrder, cap];

		// Remove from available
		availableCaps = availableCaps.filter(c => c.id !== capId);

		// Auto-submit when all caps selected
		if (selectedOrder.length === correctOrder.length) {
			currentOrder = [...selectedOrder];
			submitArrangement();
		}
	}

	// Handle Enter key in input
	function handleKeyDown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			addCapByNumber();
		}
	}

	// Remove cap from selected order (undo)
	function removeCapFromSelected(capId: number) {
		const cap = selectedOrder.find(c => c.id === capId);
		if (cap) {
			selectedOrder = selectedOrder.filter(c => c.id !== capId);
			availableCaps = [...availableCaps, cap];
		}
	}

	// Handle keyboard events for removing caps
	function handleCapKeyDown(event: KeyboardEvent, capId: number) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			removeCapFromSelected(capId);
		}
	}

	// Calculate progress percentage
	$: progressPercentage = (selectedOrder.length / correctOrder.length) * 100;

	// Calculate Score

	function calculateScore() {
		let totalError = 0;

		for (
			let i = 0;
			i < currentOrder.length;
			i++
		) {
			const correctIndex =
				correctOrder.findIndex(
					(c) =>
						c.id ===
						currentOrder[i].id
				);

			totalError += Math.abs(
				correctIndex - i
			);
		}

		tes = totalError;

		const maxError =
			currentOrder.length * MAX_ERROR_MULTIPLIER;

		accuracy = Math.max(
			0,
			100 -
				(totalError / maxError) *
					100
		);

		if (accuracy >= ACCURACY_THRESHOLD_NORMAL) {
			diagnosis =
				'Normal Color Vision';
		} else if (accuracy >= ACCURACY_THRESHOLD_MILD) {
			diagnosis =
				'Mild Color Discrimination Difficulty';
		} else {
			diagnosis =
				'Possible Color Vision Deficiency';
		}
	}

	// Submit Test

	function submitArrangement() {
		calculateScore();

		// Send completion data to backend via WebSocket - commented out
		/*
		if (ws && wsConnected) {
			try {
				ws.send(JSON.stringify({
					type: 'hue_complete',
					accuracy: accuracy,
					tesScore: tes,
					diagnosis: diagnosis,
					distance: visionDistance || 0
				}));
			} catch (error) {
				console.error('Failed to send Hue completion data:', error);
			}
		}
		*/

		submitted = true;
	}

	// Reset Test

	function resetTest() {
		testStarted = false;
		testEndedDueToNoFace = false;
		// consecutiveDistanceCount = 0; // Commented out - not used without WebSocket
		// displayDistanceStatus = 'no_face'; // Commented out - not used without WebSocket
		initializeTest();
	}

	function goToAmslerTest() {
		goto('/amsler');
	}
</script>

<div class="circular-container" in:fly={{ y: 20, duration: 600 }}>
	<div class="content-wrapper">
		{#if !testStarted && !testEndedDueToNoFace}
			<!-- Intro Screen -->
			<h1>Hue Arrangement Test</h1>
			<p class="subtitle">Color vision test with hue arrangement</p>

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

		{:else if !submitted}

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

								<!-- Available Caps -->

				<div
					class="bg-white rounded-2xl shadow-lg p-4 md:p-6 mb-6 w-4/6"
				>

					<h2
						class="text-xl md:text-2xl font-semibold mb-3 text-center"
					>
						Tap to Select
					</h2>

					<div
						class="grid grid-cols-2 lg:grid-cols-3 md:grid-cols-6 lg:grid-cols-6 gap-4 md:gap-6"
					>

						{#each availableCaps as cap}

							<button
								class="flex flex-col items-center w-full"
								on:click={() => addCapByClick(cap.id)}
								aria-label={"Select cap " + cap.id}
							>

								<div
									class="color-cap w-full aspect-square rounded-full shadow-lg border-4 border-white transition-all duration-200 hover:scale-105 active:scale-95"
									style="--cap-color: {cap.hex}"
								></div>

								<p
									class="mt-3 md:mt-4 text-2xl md:text-3xl font-bold text-gray-900"
								>
									{#if cap.id === startAnchor?.id}
										START
									{:else if cap.id === endAnchor?.id}
										END
									{:else}
										{cap.id}
									{/if}
								</p>

							</button>

						{/each}

					</div>

				</div>



				<!-- Selected Order -->

				<div
					class="bg-white rounded-2xl shadow-lg p-4 md:p-6 mb-6"
				>

					<h2
						class="text-xl md:text-2xl font-semibold mb-3 text-center"
					>
						Selected Order
					</h2>

					{#if selectedOrder.length > 0}

						<div
							class="flex flex-wrap justify-center gap-2 md:gap-3 mb-4"
						>

							{#each selectedOrder as cap, index}

								<button
									class="color-cap flex items-center justify-center w-16 h-16 md:w-20 md:h-20 rounded-full shadow-md cursor-pointer hover:shadow-lg transition active:scale-95"
									style="--cap-color: {cap.hex}"
									on:click={() => removeCapFromSelected(cap.id)}
									on:keydown={(e) => handleCapKeyDown(e, cap.id)}
									aria-label={"Remove cap " + cap.id}
								>

									<span
										class="text-xl md:text-2xl font-bold text-gray-900"
									>
										{cap.id}
									</span>

								</button>

							{/each}

						</div>

						<p
							class="text-xs md:text-sm text-gray-500 text-center"
						>
							Tap a selected cap to remove it
						</p>

					{:else}

						<p
							class="text-gray-500 italic text-center text-sm md:text-base"
						>
							No caps selected yet
						</p>

					{/if}

				</div>

				

				

			{:else}

				<!-- Results -->

				<div
					class="bg-white rounded-2xl shadow-lg p-4 md:p-8"
				>

					<h2
						class="text-2xl md:text-3xl font-bold text-gray-900 mb-6 md:mb-8 text-center"
					>
						📊 Test Results
					</h2>

					<div
						class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8"
					>

						<!-- Accuracy -->

						<div
							class="rounded-2xl p-4 md:p-6 text-center"
						>

							<h3
								class="text-base md:text-lg font-semibold mb-2"
							>
								Accuracy
							</h3>

							<p
								class="text-3xl md:text-4xl font-bold"
							>
								{accuracy.toFixed(
									1
								)}
								%
							</p>

						</div>

						<!-- TES -->

						<div
							class="rounded-2xl p-4 md:p-6 text-center"
						>

							<h3
								class="text-base md:text-lg font-semibold  mb-2"
							>
								TES Score
							</h3>

							<p
								class="text-3xl md:text-4xl font-bold"
							>
								{tes}
							</p>

						</div>

						<!-- Diagnosis -->

						<div
							class="bg-green-50 rounded-2xl p-4 md:p-6 text-center"
						>

							<h3
								class="text-base md:text-lg font-semibold text-green-900 mb-2"
							>
								Result
							</h3>

							<p
								class="text-xl md:text-2xl font-bold text-green-700"
							>
								{diagnosis}
							</p>

						</div>

					</div>

					<!-- Selected vs Correct Comparison -->

					<div class="mb-6 md:mb-8">

						

						<div
							class="flex flex-col gap-4 md:gap-6"
						>

							<!-- Selected Order -->

							<div class="bg-gray-50 rounded-2xl p-4 md:p-6">

								<h4
									class="text-lg md:text-xl font-semibold mb-3 text-center text-gray-700"
								>
									Your Selection
								</h4>

								<div
									class="flex flex-wrap justify-center gap-2 md:gap-3"
								>

									{#each currentOrder as cap}

										<div
											class="flex flex-col items-center"
										>

											<div
												class="color-cap w-12 h-12 md:w-16 md:h-16 rounded-full shadow-md"
												style="--cap-color: {cap.hex}"
											></div>

											<p
												class="mt-1 text-sm md:text-base font-bold text-gray-900"
											>
												{cap.id}
											</p>

										</div>

									{/each}

								</div>

							</div>

							<!-- Correct Order -->

							<div class="bg-gray-50 rounded-2xl p-4 md:p-6">

								<h4
									class="text-lg md:text-xl font-semibold mb-3 text-center text-gray-700"
								>
									Correct Order
								</h4>

								<div
									class="flex flex-wrap justify-center gap-2 md:gap-3"
								>

									{#each correctOrder as cap}

										<div
											class="flex flex-col items-center"
										>

											<div
												class="color-cap w-12 h-12 md:w-16 md:h-16 rounded-full shadow-md"
												style="--cap-color: {cap.hex}"
											></div>

											<p
												class="mt-1 text-sm md:text-base font-bold text-gray-900"
											>
												{cap.id}
											</p>

										</div>

									{/each}

								</div>

							</div>

						</div>

					</div>

				</div>

			{/if}
	</div>
</div>

<style>
	.content-wrapper {
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		/* padding: 40px; */
		overflow: hidden;
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

	.color-cap {
		background: var(--cap-color);
	}


</style>