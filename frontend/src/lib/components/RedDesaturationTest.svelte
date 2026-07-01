<script lang="ts">
	import { fly } from 'svelte/transition';

	type Eye = 'left' | 'right';

	// Configurable test parameters
	const SATURATION_START = 100; // Starting saturation percentage
	const SATURATION_DECREMENT = 1; // Amount to decrease per interval
	const SATURATION_MIN = 0; // Minimum saturation (stopping point)
	const INTERVAL_DURATION = 150; // Interval duration in milliseconds

	// Clinical inference thresholds
	const DIFF_THRESHOLD_NORMAL = 10; // Maximum difference for normal vision
	const DIFF_THRESHOLD_MILD = 20; // Maximum difference for mild asymmetry

	let currentEye: Eye = 'left';
	let phase: 'instructions' | 'test' | 'transition' | 'result' = 'instructions';

	let saturation = SATURATION_START;
	let interval: ReturnType<typeof setInterval>;

	let leftThreshold: number | null = null;
	let rightThreshold: number | null = null;

	function startTest() {
		phase = 'test';
		saturation = SATURATION_START;

		interval = setInterval(() => {
			if (saturation > SATURATION_MIN) {
				saturation -= SATURATION_DECREMENT;
			}
		}, INTERVAL_DURATION);
	}

	function recordThreshold() {
		if (phase !== 'test') return;

		if (currentEye === 'left') {
			leftThreshold = saturation;

			clearInterval(interval);

			currentEye = 'right';
			phase = 'transition';
		} else {
			rightThreshold = saturation;

			clearInterval(interval);
			phase = 'result';
		}
	}

	function restart() {
		clearInterval(interval);

		currentEye = 'left';
		leftThreshold = null;
		rightThreshold = null;
		saturation = SATURATION_START;
		phase = 'instructions';
	}

	function getDifference() {
		if (leftThreshold === null || rightThreshold === null) return 0;
		return Math.abs(leftThreshold - rightThreshold);
	}

	function getInference() {
		const diff = getDifference();

		if (diff < DIFF_THRESHOLD_NORMAL) {
			return {
				status: 'Normal',
				recommendation:
					'No significant red desaturation detected.'
			};
		}

		if (diff < DIFF_THRESHOLD_MILD) {
			return {
				status: 'Mild Asymmetry',
				recommendation:
					'Mild difference detected between eyes. Monitor vision changes.'
			};
		}

		return {
			status: 'Significant Asymmetry',
			recommendation:
				'Consider a professional eye examination for optic nerve assessment.'
		};
	}

	function handleKey(event: KeyboardEvent) {
		if (event.code !== 'Space') return;

		if (phase === 'instructions') {
			startTest();
		} else if (phase === 'test') {
			recordThreshold();
		} else if (phase === 'transition') {
			startTest();
		}
	}
</script>

<svelte:window on:keydown={handleKey} />

<svelte:head>
	<title>Red Desaturation Test</title>
</svelte:head>

<div class="container" in:fly={{ y: 20, duration: 500 }}>
	<h1>Red Desaturation Test</h1>

	{#if phase === 'instructions'}
		<div class="card">
			{#if currentEye === 'left'}
				<h2>Left Eye Test</h2>

				<p>
					Cover your RIGHT eye.
				</p>

				<p>
					Look at the red circle using only your LEFT eye.
				</p>

				<p class="hint">
					Press SPACE to begin.
				</p>
			{:else}
				<h2>Right Eye Test</h2>

				<p>
					Cover your LEFT eye.
				</p>

				<p>
					Look at the red circle using only your RIGHT eye.
				</p>

				<p class="hint">
					Press SPACE to begin.
				</p>
			{/if}
		</div>
	{/if}

	{#if phase === 'transition'}
		<div class="card">
			<h2>Left Eye Complete</h2>

			<div class="metric">
				Left Eye Threshold:
				<strong>{leftThreshold}%</strong>
			</div>

			<p>
				Cover your LEFT eye.
			</p>

			<p>
				Look at the red circle using only your RIGHT eye.
			</p>

			<p class="hint">
				Press SPACE to begin right eye test.
			</p>
		</div>
	{/if}

	{#if phase === 'test'}
		<div class="card">
			<h2>
				Testing {currentEye === 'left' ? 'Left Eye' : 'Right Eye'}
			</h2>

			<div
				class="red-circle"
				style="background-color:hsl(0, {saturation}%, 50%)"
			></div>

			<div class="value">
				Current Saturation: {saturation}%
			</div>

			<p>
				Press SPACE when the red circle becomes too faint to clearly
				recognize as red.
			</p>
		</div>
	{/if}

	{#if phase === 'result'}
		<div class="card result">
			<h2>Results</h2>

			<div class="metric">
				Left Eye Threshold:
				<strong>{leftThreshold}%</strong>
			</div>

			<div class="metric">
				Right Eye Threshold:
				<strong>{rightThreshold}%</strong>
			</div>

			<div class="metric">
				Difference:
				<strong>{getDifference()}%</strong>
			</div>

			<div class="status">
				{getInference().status}
			</div>

			<p>
				{getInference().recommendation}
			</p>

			<div class="button-group">
				<button on:click={restart}>
					🔄 Retake Test
				</button>
				<a href="/" class="home-button">🏠 Back to Home</a>
			</div>
		</div>
	{/if}
</div>

<style>
	.container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
	}

	h1 {
		margin-bottom: 2rem;
		color: white;
		font-size: 2.5rem;
		font-weight: 700;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
	}

	.card {
		background: white;
		padding: 3rem;
		border-radius: 24px;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		text-align: center;
		max-width: 600px;
		width: 100%;
		backdrop-filter: blur(10px);
	}

	.card h2 {
		color: #333;
		font-size: 2rem;
		margin-bottom: 1.5rem;
		font-weight: 600;
	}

	.card p {
		color: #666;
		font-size: 1.1rem;
		line-height: 1.6;
		margin-bottom: 1rem;
	}

	.red-circle {
		width: 300px;
		height: 300px;
		border-radius: 50%;
		margin: 2rem auto;
		border: 4px solid #e0e0e0;
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
		transition: all 0.3s ease;
	}

	.red-circle:hover {
		transform: scale(1.05);
		box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
	}

	.value {
		font-size: 1.5rem;
		font-weight: bold;
		margin-bottom: 1.5rem;
		color: #333;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.metric {
		margin: 1.5rem 0;
		font-size: 1.2rem;
		color: #555;
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 12px;
		border-left: 4px solid #667eea;
	}

	.metric strong {
		color: #333;
		font-size: 1.4rem;
	}

	.status {
		font-size: 1.8rem;
		font-weight: bold;
		margin: 2rem 0;
		padding: 1rem;
		border-radius: 12px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
	}

	.hint {
		margin-top: 2rem;
		font-weight: bold;
		color: #667eea;
		font-size: 1.2rem;
		padding: 1rem;
		background: #f0f4ff;
		border-radius: 12px;
		border: 2px dashed #667eea;
	}

	button {
		padding: 1rem 2rem;
		border: none;
		border-radius: 12px;
		cursor: pointer;
		font-size: 1.1rem;
		font-weight: 600;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		transition: all 0.3s ease;
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
		margin-top: 1.5rem;
	}

	button:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
	}

	button:active {
		transform: translateY(0);
	}

	.button-group {
		display: flex;
		gap: 12px;
		justify-content: center;
		align-items: center;
	}

	.home-button {
		padding: 1rem 2rem;
		background: #6b7280;
		color: white;
		text-decoration: none;
		border: none;
		border-radius: 12px;
		font-size: 1.1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		display: inline-block;
	}

	.home-button:hover {
		background: #4b5563;
		transform: translateY(-2px);
	}

	.result {
		background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
	}
</style>