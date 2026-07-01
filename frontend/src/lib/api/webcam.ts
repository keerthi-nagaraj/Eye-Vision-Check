import { apiUrl } from "$lib/config/api";

export type ServerVisionResult = {
	faceDetected: boolean;
	distanceCm: number;
	opencvBrightness: number;
	tensorflowMean: number;
	score: number;
};

export async function analyzeFrameOnServer(
	canvas: HTMLCanvasElement
): Promise<ServerVisionResult | null> {
	try {
		const dataUrl = canvas.toDataURL("image/jpeg", 0.85);
		const res = await fetch(apiUrl("/webcam/analyze-frame"), {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ image: dataUrl }),
		});
		if (!res.ok) return null;
		return (await res.json()) as ServerVisionResult;
	} catch {
		return null;
	}
}
