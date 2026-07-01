export const IDEAL_FACE_WIDTH_PX = 120;
export const IDEAL_DISTANCE_CM = 90;

export function distanceCmFromFaceWidthPx(faceWidthPx: number): number {
	if (faceWidthPx <= 0) return 0;

	const cm =
		IDEAL_DISTANCE_CM *
		(IDEAL_FACE_WIDTH_PX / faceWidthPx);

	return Math.min(200, Math.max(15, cm));
}

export function getFaceWidthPx(landmarks: any[], width: number): number {
	if (!landmarks?.length) return 0;

	// MediaPipe face landmarks for face width
	// 33 = bridge of nose (left side)
	// 263 = bridge of nose (right side)
	// These two points form the horizontal width of the face at the bridge of the nose
	const left = landmarks[33];
	const right = landmarks[263];

	if (!left || !right) return 0;

	return Math.abs((right.x - left.x) * width);
}