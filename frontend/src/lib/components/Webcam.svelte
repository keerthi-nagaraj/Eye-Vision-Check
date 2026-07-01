<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	export let showColorTest = false;

	let video: HTMLVideoElement;
	let canvas: HTMLCanvasElement;

	let stream: MediaStream | null = null;

	let isActive = false;
	let error = '';

	let currentColor = '';
	let colorBlindnessType = '';

	onMount(() => {
		startCamera();

		return () => {
			stopCamera();
		};
	});

	async function startCamera() {
		try {
			stream = await navigator.mediaDevices.getUserMedia({
				video: {
					width: { ideal: 640 },
					height: { ideal: 480 },
					facingMode: 'user'
				}
			});

			if (video) {
				video.srcObject = stream;
				isActive = true;
				error = '';
			}
		} catch (err) {
			error =
				'Unable to access camera. Please allow camera permission.';
			console.error(err);
		}
	}

	function stopCamera() {
		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
			stream = null;
		}

		isActive = false;
	}

	function captureFrame() {
		if (!video || !canvas) return;

		const ctx = canvas.getContext('2d');

		if (!ctx) return;

		canvas.width = video.videoWidth;
		canvas.height = video.videoHeight;

		ctx.drawImage(video, 0, 0);

		if (showColorTest) {
			analyzeColors(ctx, canvas.width, canvas.height);
		}
	}

	function analyzeColors(
		ctx: CanvasRenderingContext2D,
		width: number,
		height: number
	) {
		const imageData = ctx.getImageData(0, 0, width, height);

		const data = imageData.data;

		let redTotal = 0;
		let greenTotal = 0;
		let blueTotal = 0;

		const pixelCount = data.length / 4;

		for (let i = 0; i < data.length; i += 4) {
			redTotal += data[i];
			greenTotal += data[i + 1];
			blueTotal += data[i + 2];
		}

		const avgRed = redTotal / pixelCount;
		const avgGreen = greenTotal / pixelCount;
		const avgBlue = blueTotal / pixelCount;

		currentColor = `rgb(${Math.round(avgRed)}, ${Math.round(avgGreen)}, ${Math.round(avgBlue)})`;

		const redGreenRatio = avgRed / (avgGreen || 1);
		const blueYellowRatio =
			avgBlue / ((avgRed + avgGreen) / 2 || 1);

		if (redGreenRatio > 1.5) {
			colorBlindnessType =
				'Possible protanopia (red-blind)';
		} else if (redGreenRatio < 0.7) {
			colorBlindnessType =
				'Possible deuteranopia (green-blind)';
		} else if (blueYellowRatio > 1.3) {
			colorBlindnessType =
				'Possible tritanopia (blue-blind)';
		} else {
			colorBlindnessType =
				'Normal color vision detected';
		}
	}

	function toggleColorTest() {
		showColorTest = !showColorTest;

		if (showColorTest) {
			captureFrame();
		}
	}

	onDestroy(() => {
		stopCamera();
	});
</script>

<div class="flex flex-col items-center space-y-4">
	<div class="relative">
		<video
			bind:this={video}
			autoplay
			playsinline
			class="rounded-xl border-2 border-gray-300 shadow-lg w-full max-w-[640px]"
		></video>

		<canvas bind:this={canvas} class="hidden"></canvas>

		{#if isActive}
			<div class="absolute top-4 right-4">
				<div
					class="h-3 w-3 animate-pulse rounded-full bg-red-500"
				></div>
			</div>
		{/if}
	</div>

	<div class="flex gap-4">
		<button
			on:click={captureFrame}
			class="rounded-lg bg-blue-600 px-5 py-2 text-white"
		>
			Capture
		</button>

		<button
			on:click={toggleColorTest}
			class="rounded-lg bg-green-600 px-5 py-2 text-white"
		>
			{showColorTest ? 'Stop Test' : 'Start Test'}
		</button>

		<button
			on:click={stopCamera}
			class="rounded-lg bg-red-600 px-5 py-2 text-white"
		>
			Stop
		</button>
	</div>

	{#if currentColor}
		<div
			class="w-full max-w-md rounded-xl border bg-white p-5 shadow"
		>
			<h3 class="mb-4 text-lg font-bold">
				Color Analysis
			</h3>

			<div class="flex items-center gap-4">
				<div
					class="h-16 w-16 rounded-lg border"
					style={`background:${currentColor}`}
				></div>

				<div>
					<p>{currentColor}</p>

					<p class="font-semibold">
						{colorBlindnessType}
					</p>
				</div>
			</div>
		</div>
	{/if}

	{#if error}
		<p class="text-red-600">{error}</p>
	{/if}
</div>