<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { goto } from '$app/navigation';

	let { onComplete } = $props();
	let loadingProgress = $state(0);

	onMount(() => {
		// Show splash screen for 30 seconds
		const duration = 10000; // 30 seconds
		const updateInterval = 100; // Update every 300ms
		const progressIncrement = 100 / (duration / updateInterval);

		const interval = setInterval(() => {
			loadingProgress += progressIncrement;
			if (loadingProgress >= 100) {
				loadingProgress = 100;
				clearInterval(interval);
				setTimeout(() => {
					if (onComplete) {
						onComplete();
					}
				}, 500);
			}
		}, updateInterval);

		return () => clearInterval(interval);
	});
</script>

<div class="splash-screen" in:fade={{ duration: 800 }} out:fade={{ duration: 500 }}>
	<div class="logo-container" in:fly={{ y: -50, duration: 1000, delay: 200 }}>
		<div class="eye-logo">
			<div class="eye-outer">
				<div class="eye-inner">
					<div class="pupil"></div>
				</div>
			</div>
		</div>
	</div>

	<h1 class="app-title" in:fly={{ y: 30, duration: 1000, delay: 400 }}>
		Eye Vision Test
	</h1>

	<p class="app-subtitle" in:fly={{ y: 30, duration: 1000, delay: 600 }}>
		Comprehensive Eye Screening Platform
	</p>

	<div class="loading-bar-container" in:fade={{ duration: 800, delay: 800 }}>
		<div class="loading-bar">
			<div class="loading-progress" style="width: {loadingProgress}%"></div>
		</div>
		<p class="loading-text">Loading... {Math.round(loadingProgress)}%</p>
	</div>
</div>

<style>
	.splash-screen {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 1080px;
		height: 1080px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		z-index: 9999;
		border-radius: 50%;
	}

	.logo-container {
		margin-bottom: 40px;
	}

	.eye-logo {
		width: 120px;
		height: 120px;
		position: relative;
		animation: pulse 8s ease-in-out infinite;
	}

	.eye-outer {
		width: 100%;
		height: 100%;
		background: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
	}

	.eye-inner {
		width: 70%;
		height: 70%;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.pupil {
		width: 40%;
		height: 40%;
		background: #1a1a2e;
		border-radius: 50%;
		box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
	}

	@keyframes pulse {
		0%, 100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.05);
		}
	}

	.app-title {
		font-size: 48px;
		font-weight: 800;
		color: white;
		margin: 0 0 16px 0;
		text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
		letter-spacing: 2px;
	}

	.app-subtitle {
		font-size: 18px;
		color: rgba(255, 255, 255, 0.9);
		margin: 0 0 60px 0;
		font-weight: 500;
		letter-spacing: 1px;
	}

	.loading-bar-container {
		width: 300px;
		text-align: center;
	}

	.loading-bar {
		width: 100%;
		height: 6px;
		background: rgba(255, 255, 255, 0.3);
		border-radius: 3px;
		overflow: hidden;
		margin-bottom: 16px;
	}

	.loading-progress {
		height: 100%;
		background: white;
		border-radius: 3px;
		transition: width 0.1s linear;
		box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
	}

	.loading-text {
		font-size: 14px;
		color: rgba(255, 255, 255, 0.8);
		margin: 0;
		font-weight: 500;
	}
</style>
