"""
Webcam frame analysis: OpenCV + MediaPipe + TensorFlow (server-side).
"""

from __future__ import annotations

import base64
import os

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

IDEAL_FACE_WIDTH_PX = 120
IDEAL_DISTANCE_CM = 90

MODEL_PATH = os.environ.get(
	"BLAZE_FACE_MODEL",
	"/app/models/blaze_face_short_range.tflite",
)

_detector: vision.FaceDetector | None = None


def _get_detector() -> vision.FaceDetector:
	global _detector
	if _detector is None:
		if not os.path.isfile(MODEL_PATH):
			raise FileNotFoundError(f"Face model not found: {MODEL_PATH}")
		base = python.BaseOptions(model_asset_path=MODEL_PATH)
		opts = vision.FaceDetectorOptions(base_options=base)
		_detector = vision.FaceDetector.create_from_options(opts)
	return _detector


def _distance_cm(face_width_px: float) -> float:
	if face_width_px <= 0:
		return 0.0
	cm = IDEAL_DISTANCE_CM * (IDEAL_FACE_WIDTH_PX / face_width_px)
	return float(min(200.0, max(15.0, cm)))


def analyze_frame_bytes(image_bytes: bytes) -> dict:
	arr = np.frombuffer(image_bytes, dtype=np.uint8)
	bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
	if bgr is None:
		return {"error": "opencv_decode_failed", "faceDetected": False}

	h, w = bgr.shape[:2]
	rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
	gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
	opencv_brightness = float(np.mean(gray))

	tensor = tf.convert_to_tensor(rgb, dtype=tf.float32)
	tensorflow_mean = float(tf.reduce_mean(tensor).numpy())

	mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
	result = _get_detector().detect(mp_image)

	distance_cm = 0.0
	score = 0.0
	face_detected = False

	if result.detections:
		det = result.detections[0]
		face_detected = True
		box = det.bounding_box
		face_w = float(box.width)
		if face_w <= 1:
			face_w = face_w * w
		distance_cm = _distance_cm(face_w)
		if det.categories:
			score = float(det.categories[0].score)

	return {
		"faceDetected": face_detected,
		"distanceCm": round(distance_cm, 1),
		"opencvBrightness": round(opencv_brightness, 1),
		"tensorflowMean": round(tensorflow_mean, 1),
		"score": round(score, 3),
	}
