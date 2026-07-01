<script lang="ts">
	import Sidebar from "$lib/components/Sidebar.svelte";
	import { fly } from "svelte/transition";
	import { goto } from "$app/navigation";
	import { onMount, onDestroy } from "svelte";
	import { submitTestResult } from "$lib/api/results";

	import { initFaceMesh, stopFaceMesh } from "$lib/services/faceMesh";
	import { computeAverageBrightness } from "$lib/services/opencv";

	import {
		getFaceWidthPx,
		distanceCmFromFaceWidthPx,
	} from "$lib/services/calibration";

	let videoElement: HTMLVideoElement;
	let faceBox: {
		x: number;
		y: number;
		width: number;
		height: number;
	} | null = null;
	let canvasElement: HTMLCanvasElement;

	let stream: MediaStream | null = null;

	let status = "Initializing...";
	let statusColor = "#ef4444";

	let averageDistance = 0;
	let landmarkCount = 0;
	let landmarks: any[] = [];
	let brightnessWarning = false;

	let isDetecting = false;
	let animationFrameId = 0;
	let distanceHistory: number[] = [];

	// ---------------- CAMERA ----------------
	async function startCamera() {
		if (
			typeof navigator === "undefined" ||
			!navigator.mediaDevices?.getUserMedia
		) {
			status = "Camera not supported";
			statusColor = "#ef4444";
			return;
		}

		try {
			stream = await navigator.mediaDevices.getUserMedia({
				video: {
					width: { ideal: 640 },
					height: { ideal: 480 },
					facingMode: "user",
				},
				audio: false,
			});

			videoElement.srcObject = stream;
			videoElement.muted = true;
			videoElement.playsInline = true;

			await videoElement.play();

			status = "Camera Ready";
			statusColor = "#22c55e";
			isDetecting = true;

			// ---------------- AI START ----------------
			await initFaceMesh(videoElement, ({ landmarks: lm, bbox }) => {
				landmarks = lm;
				faceBox = bbox ?? null;
				landmarkCount = lm?.length ?? 0;
				// rawAvgDistance retained for compatibility but not updated here
				// Compute distance based on face width if needed
				if (lm && lm.length > 263) {
					const left = lm[33];
					const right = lm[263];
					const faceWidthPx = Math.abs(
						(right.x - left.x) * canvasElement.width,
					);
					if (faceWidthPx > 0) {
						averageDistance =
							distanceCmFromFaceWidthPx(faceWidthPx);
					} else {
						// fallback: keep previous averageDistance
					}
				}
			});

			processFrame();
		} catch (e) {
			console.error(e);
			status = "Camera access denied";
			statusColor = "#ef4444";
		}
	}

	// ---------------- RENDER LOOP ----------------
	function processFrame() {
		if (!isDetecting) return;

		const ctx = canvasElement.getContext("2d");
		if (!ctx) return;

		if (videoElement.readyState < 2 || videoElement.videoWidth === 0) {
			animationFrameId = requestAnimationFrame(processFrame);
			return;
		}

		canvasElement.width = videoElement.videoWidth;
		canvasElement.height = videoElement.videoHeight;

		ctx.drawImage(videoElement, 0, 0);

		// ---------------- BRIGHTNESS CHECK ----------------
		const imageData = ctx.getImageData(
			0,
			0,
			canvasElement.width,
			canvasElement.height,
		);

		const brightness = computeAverageBrightness(imageData);
		brightnessWarning = brightness < 50;

		// ---------------- DRAW LANDMARKS ----------------
		if (landmarks?.length) {
			ctx.fillStyle = "rgba(255,0,0,0.7)";
			const radius = Math.max(1, canvasElement.width / 800);

			for (const lm of landmarks) {
				const x = lm.x * canvasElement.width;
				const y = lm.y * canvasElement.height;

				ctx.beginPath();
				ctx.arc(x, y, radius, 0, Math.PI * 2);
				ctx.fill();
			}
			// Draw bounding box if available
			if (faceBox) {
				ctx.strokeStyle = "rgba(0,255,0,0.8)";
				ctx.lineWidth = 3;
				ctx.strokeRect(
					faceBox.x * canvasElement.width,
					faceBox.y * canvasElement.height,
					faceBox.width * canvasElement.width,
					faceBox.height * canvasElement.height,
				);
			}
		} else {
			ctx.fillStyle = "rgba(255,255,0,0.6)";
			ctx.font = "20px sans-serif";
			ctx.fillText("No face detected", 20, 30);
			// No landmarks – indicate face not detected for UI warning
		}

		// ---------------- SMOOTH DISTANCE ----------------
		distanceHistory.push(averageDistance);
		if (distanceHistory.length > 15) distanceHistory.shift();

		const avg =
			distanceHistory.reduce((a, b) => a + b, 0) / distanceHistory.length;

		// ---------------- STATUS LOGIC ----------------
		if (avg >= 70 && avg <= 100) {
			status = `PERFECT: ${avg.toFixed(1)} cm`;
			statusColor = "#22c55e";
		} else if (avg < 70) {
			status = `TOO CLOSE: ${avg.toFixed(1)} cm`;
			statusColor = "#f97316";
		} else {
			status = `TOO FAR: ${avg.toFixed(1)} cm`;
			statusColor = "#eab308";
		}

		animationFrameId = requestAnimationFrame(processFrame);
	}

	// ---------------- SAVE RESULT ----------------
	async function saveWebcamResult() {
		await submitTestResult({
			testType: "webcam",
			result: status,
			score:
				averageDistance >= 60 && averageDistance <= 90
					? 100
					: averageDistance >= 50 && averageDistance <= 100
						? 75
						: 50,
			totalQuestions: 1,
			correctAnswers:
				averageDistance >= 60 && averageDistance <= 90 ? 1 : 0,
			testData: {
				webcamStatus: status,
				averageDistance: Number(averageDistance.toFixed(1)),
				brightness: brightnessWarning ? "Low Light" : "Good Lighting",
			},
			difficulty: "standard",
			details: {
				webcamStatus: status,
				averageDistance: Number(averageDistance.toFixed(1)),
				brightness: brightnessWarning ? "Low Light" : "Good Lighting",
			},
		});
	}

	async function startTest() {
		await saveWebcamResult();
		await new Promise((r) => setTimeout(r, 300));
		goto("/ishihara");
	}

	// ---------------- LIFECYCLE ----------------
	onMount(() => {
		startCamera();
	});

	onDestroy(() => {
		isDetecting = false;
		stopFaceMesh();
		cancelAnimationFrame(animationFrameId);
		stream?.getTracks().forEach((t) => t.stop());
	});
</script>

<!-- ================= UI ================= -->
<div class="flex flex-col items-center justify-center h-full bg-gray-100" in:fly={{ y: 20, duration: 600 }}>
	<div class="w-full max-w-lg px-4">
		<!-- Header -->
		<div class="mb-4 text-center">
			<h1 class="mb-2 text-xl font-bold text-gray-900">
				Webcam Calibration
			</h1>
			<p class="text-sm text-gray-600">
				Maintain proper distance for accurate testing.
			</p>
		</div>

			<!-- Instructions -->
			<div class="mb-4 rounded-2xl bg-white p-4 shadow-lg">
				<h2 class="mb-2 text-sm font-semibold">Instructions</h2>
				<ul class="space-y-1 text-sm text-gray-700">
					<li>• Sit in a well-lit environment</li>
					<li>• Keep your face centered</li>
					<li>• Maintain 60–90 cm distance</li>
				</ul>
			</div>

			<!-- Video + Canvas -->
			<div
				class="relative overflow-hidden rounded-2xl bg-white p-4 shadow-xl"
			>
				<video bind:this={videoElement} class="hidden" playsinline muted
				></video>

				<canvas
					bind:this={canvasElement}
					class="h-[300px] w-[400px] rounded-xl bg-black mx-auto"
				></canvas>

				<!-- Status -->
				<div
					class="absolute left-2 top-2 rounded-lg px-3 py-2 text-sm font-bold text-white shadow-lg"
					style="background:{statusColor}"
				>
					{status}
				</div>

				<!-- Distance -->
				<div
					class="absolute right-2 top-2 rounded-lg bg-black/70 px-3 py-2 text-white shadow-lg"
				>
					<p class="text-sm text-gray-300">Distance</p>
					<p class="text-lg font-bold">
						{averageDistance.toFixed(1)} cm
					</p>
				</div>

				<!-- Brightness warning -->
				{#if brightnessWarning}
					<div
						class="absolute bottom-2 left-2 right-2 rounded-lg bg-black/80 px-3 py-2 text-sm font-semibold text-yellow-400 z-10"
					>
						⚠️ Environment too dark
					</div>
				{/if}
				{#if !landmarks?.length}
					<div
						class="absolute bottom-2 left-2 right-2 rounded-lg bg-red-700/80 px-3 py-2 text-sm font-semibold text-white z-10"
					>
						⚠️ No face detected
					</div>
				{/if}
			</div>

			<!-- Debug -->
			<div class="mt-2 text-sm text-gray-600 text-center">
				<p>Landmarks: {landmarkCount}</p>
			</div>

			<!-- Button -->
			<div class="mt-4 flex justify-center">
				<button
					on:click={startTest}
					class="rounded-lg bg-green-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-green-700"
				>
					Start Test
				</button>
			</div>
		</div>
	</div>
