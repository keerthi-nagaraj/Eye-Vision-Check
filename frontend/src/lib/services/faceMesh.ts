import { FilesetResolver, FaceLandmarker } from "@mediapipe/tasks-vision";

export type FaceMeshResult = {
	landmarks: any[];
	bbox?: { x: number; y: number; width: number; height: number };
};

let faceLandmarker: FaceLandmarker | null = null;
let running = false;

export async function initFaceMesh(
	video: HTMLVideoElement,
	onResults: (result: FaceMeshResult) => void
) {
	if (faceLandmarker || running) return;
	running = true;

	const vision = await FilesetResolver.forVisionTasks(
		"https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
		// MediaPipe Vision WASM files (runs AI vision models in browser)
		// Used for face detection, hand tracking, pose estimation, etc.
		// Enables fast real-time webcam processing using WebAssembly
	);

	faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
		baseOptions: {
			modelAssetPath:
				"https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
			// MediaPipe Face Landmarker AI model
			// Used for real-time face detection and 3D face mesh tracking
			// Detects facial landmarks such as eyes, nose, lips, iris, and jawline
			// Required for webcam-based face analysis, gaze tracking, and head movement detection
			// Loaded from Google's hosted MediaPipe model storage
		},
		runningMode: "VIDEO",
		numFaces: 1
	});

	const loop = () => {
		if (!running || !faceLandmarker) return;

		if (video.readyState >= 2) {
			const result = faceLandmarker.detectForVideo(video, Date.now());

			if (result.faceLandmarks?.length) {
				const landmarks = result.faceLandmarks[0];
				// Compute bounding box (normalized coordinates)
				let minX = 1, minY = 1, maxX = 0, maxY = 0;
				for (const lm of landmarks) {
					if (lm.x < minX) minX = lm.x;
					if (lm.y < minY) minY = lm.y;
					if (lm.x > maxX) maxX = lm.x;
					if (lm.y > maxY) maxY = lm.y;
				}
				const bbox = {
					x: minX,
					y: minY,
					width: maxX - minX,
					height: maxY - minY,
				};
				onResults({
					landmarks,
					bbox,
				});
			}
		}

		requestAnimationFrame(loop);
	};

	loop();
}

export function stopFaceMesh() {
	running = false;
	faceLandmarker = null;
}