"""
Flask API server for Color Vision Test Suite.

Supports:
- Ishihara Test
- Tritan Test
- Hue Test
- Amsler Grid Test
- Webcam Test
- Contrast Sensitivity Test
- Visual Acuity Test

Database:
- SQLite only
"""

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

import os
import random
import uuid
import base64

from datetime import datetime
from dotenv import load_dotenv

import database as db
import openai

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# OPENAI CONFIG
# =========================================================

openai.api_key = os.getenv("OPENAI_API_KEY")

# =========================================================
# APP
# =========================================================

app = Flask(__name__)

# =========================================================
# CORS
# =========================================================

CORS(
    app,
    origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    supports_credentials=True
)

# =========================================================
# INIT DATABASE
# =========================================================

db.create_tables()

print("===================================")
print("✅ SQLite Database Connected")
print("📁 Database:", db.DB_PATH)
print("===================================")

# =========================================================
# HELPERS
# =========================================================

def now():
    return datetime.now().isoformat()


def generate_id():
    return str(uuid.uuid4())


def parse_test_body(body):

    body = body or {}

    return {
        "user_id": body.get("user_id")
                    or body.get("userId")
                    or "anonymous",

        "test_type": body.get("test_type")
                     or body.get("testType")
                     or "unknown",

        "score": float(body.get("score", 0)),

        "diagnosis": body.get("diagnosis")
                       or body.get("result")
                       or "",

        "total_questions": int(
            body.get("total_questions")
            or body.get("totalQuestions")
            or 0
        ),

        "correct_answers": int(
            body.get("correct_answers")
            or body.get("correctAnswers")
            or 0
        ),

        "difficulty": body.get("difficulty", "standard"),

        "duration_seconds": int(
            body.get("duration_seconds")
            or body.get("durationSeconds")
            or 0
        ),

        "test_data": body.get("test_data")
                     or body.get("testData")
                     or {}
    }

# =========================================================
# ROOT
# =========================================================

@app.route("/")
def home():
    return jsonify({
        "message": "Color Vision Test API",
        "database": "SQLite",
        "database_file": db.DB_PATH,
        "status": "running"
    })

# =========================================================
# HEALTH
# =========================================================

@app.route("/api/health")
def health():
    return jsonify({
        "success": True,
        "database": "sqlite",
        "timestamp": now(),
        "status": "healthy"
    })

# =========================================================
# SUBMIT TEST RESULT
# =========================================================

@app.route("/api/tests/submit", methods=["POST"])
def submit_test():

    try:
        body = request.get_json()

        data = parse_test_body(body)

        user_id = data["user_id"]

        session_user = logged_in_user_id()

        if session_user and user_id == "anonymous":
            user_id = session_user

        result_id = generate_id()

        timestamp = now()

        db.save_test_result(
            result_id=result_id,
            user_id=user_id,
            test_type=data["test_type"],
            score=data["score"],
            diagnosis=data["diagnosis"],
            total_questions=data["total_questions"],
            correct_answers=data["correct_answers"],
            difficulty=data["difficulty"],
            duration_seconds=data["duration_seconds"],
            test_data=data["test_data"],
            timestamp=timestamp
        )

        return jsonify({
            "success": True,
            "message": "Result saved successfully",
            "data": {
                "id": result_id,
                "user_id": user_id,
                "test_type": data["test_type"],
                "score": data["score"],
                "diagnosis": data["diagnosis"],
                "timestamp": timestamp
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# GET RESULTS
# =========================================================

@app.route("/api/results/")
def get_results():

    try:
        user_id = request.args.get("user_id", "anonymous")
        test_type = request.args.get("test_type")

        limit = int(request.args.get("limit", 100))
        page = int(request.args.get("page", 1))

        offset = (page - 1) * limit

        results = db.get_test_results(
            user_id=user_id,
            test_type=test_type,
            limit=limit,
            offset=offset
        )

        total = db.count_test_results(
            user_id=user_id,
            test_type=test_type
        )

        return jsonify({
            "success": True,
            "data": {
                "results": results,
                "total": total,
                "page": page,
                "limit": limit
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================================================
# DELETE RESULT
# =========================================================

@app.route("/api/results/<result_id>", methods=["DELETE"])
def delete_result(result_id):

    deleted = db.delete_test_result(result_id)

    if not deleted:
        return jsonify({
            "success": False,
            "message": "Result not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Result deleted successfully"
    })

# =========================================================
# CLEAR RESULTS
# =========================================================

@app.route("/api/results/clear", methods=["DELETE"])
def clear_results():

    user_id = request.args.get("user_id", "anonymous")

    deleted = db.clear_test_results(user_id)

    return jsonify({
        "success": True,
        "message": f"{deleted} results cleared"
    })

# =========================================================
# RESULTS STATS
# =========================================================

@app.route("/api/results/stats")
def get_stats():

    stats = db.get_test_stats()

    return jsonify({
        "success": True,
        "data": stats
    })

# =========================================================
# USER COUNT
# =========================================================

@app.route("/api/users/count")
def get_user_count():

    return jsonify({
        "success": True,
        "data": {
            "user_count": 0
        }
    })

# =========================================================
# ISHIHARA TEST
# =========================================================

@app.route("/api/tests/generate/ishihara")
def generate_ishihara():

    round_num = int(request.args.get("round", 1))

    target = random.randint(1, 99)

    return jsonify({
        "success": True,
        "data": {
            "round": round_num,
            "target_number": target,
            "difficulty": request.args.get("difficulty", "standard"),
            "pattern": {
                "background_dots": [],
                "number_dots": []
            }
        }
    })

# =========================================================
# TRITAN TEST
# =========================================================

@app.route("/api/tests/generate/tritan")
def generate_tritan():

    round_num = int(request.args.get("round", 1))

    return jsonify({
        "success": True,
        "data": {
            "round": round_num,
            "target_number": random.randint(1, 99),
            "pattern": {
                "background_dots": [],
                "number_dots": []
            }
        }
    })

# =========================================================
# HUE TEST
# =========================================================

@app.route("/api/tests/generate/hue")
def generate_hue():

    round_num = int(request.args.get("round", 1))

    num_caps = int(request.args.get("num_caps", 16))

    colors = []

    for i in range(num_caps):

        hue = (i / num_caps) * 0.8

        rgb = colorsys.hls_to_rgb(hue, 0.5, 0.6)

        hex_color = '#%02x%02x%02x' % (
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )

        colors.append({
            "id": i,
            "hex": hex_color,
            "hue": hue
        })

    return jsonify({
        "success": True,
        "data": {
            "round": round_num,
            "colors": colors,
            "correct_order": colors
        }
    })

# =========================================================
# WEBCAM ANALYSIS
# =========================================================

@app.route("/api/webcam/analyze-frame", methods=["POST"])
def analyze_webcam_frame():
    """OpenCV + MediaPipe + TensorFlow analysis of a single webcam frame."""
    try:
        from vision_pipeline import analyze_frame_bytes

        body = request.get_json(silent=True) or {}
        image_data = body.get("image", "")
        if not image_data:
            return jsonify({"error": "missing image"}), 400

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        raw = base64.b64decode(image_data)
        result = analyze_frame_bytes(raw)
        if result.get("error"):
            return jsonify(result), 400
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================================
# AI RECOMMENDATIONS FOR VISUAL ACUITY
# =========================================================

@app.route("/api/ai/vision-recommendations", methods=["POST"])
def generate_vision_recommendations():
    """Generate AI-powered vision recommendations using OpenAI."""
    try:
        body = request.get_json()

        if not body:
            return jsonify({"error": "missing request body"}), 400

        # Extract test data
        overall_accuracy = body.get("overallAccuracy", 0)
        large_accuracy = body.get("largeAccuracy", 0)
        medium_accuracy = body.get("mediumAccuracy", 0)
        small_accuracy = body.get("smallAccuracy", 0)
        large_correct = body.get("largeCorrect", 0)
        large_incorrect = body.get("largeIncorrect", 0)
        medium_correct = body.get("mediumCorrect", 0)
        medium_incorrect = body.get("mediumIncorrect", 0)
        small_correct = body.get("smallCorrect", 0)
        small_incorrect = body.get("smallIncorrect", 0)
        avg_response_time = body.get("averageResponseTime", 0)

        # Create prompt for AI
        prompt = f"""You are an expert optometrist and vision specialist. Analyze the following visual acuity test results and provide personalized recommendations.

Test Results:
- Overall Accuracy: {overall_accuracy}%
- Large Targets (100-120px): {large_accuracy}% accuracy ({large_correct}/8 correct, {large_incorrect}/8 incorrect)
- Medium Targets (60-80px): {medium_accuracy}% accuracy ({medium_correct}/8 correct, {medium_incorrect}/8 incorrect)
- Small Targets (20-50px): {small_accuracy}% accuracy ({small_correct}/8 correct, {small_incorrect}/8 incorrect)
- Average Response Time: {avg_response_time}ms

Please provide:
1. A brief vision category assessment (e.g., Normal Vision, Possible Myopia, Possible Hyperopia, General Vision Weakness)
2. 3-5 specific, actionable recommendations based on the performance patterns
3. Any specific observations about the performance across different size groups

Keep the recommendations professional, medically sound, and practical. Do not make definitive diagnoses - suggest possibilities and recommend professional consultation when appropriate.

Format your response as JSON with this structure:
{{
  "visionCategory": "assessment here",
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
}}"""

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert optometrist providing vision test analysis and recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        # Parse the response
        ai_response = response.choices[0].message.content

        # Try to extract JSON from the response
        import json
        import re

        # Look for JSON pattern in the response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            try:
                result_data = json.loads(json_match.group())
                return jsonify({
                    "success": True,
                    "data": result_data
                })
            except json.JSONDecodeError:
                pass

        # If JSON parsing fails, return the raw text
        return jsonify({
            "success": True,
            "data": {
                "visionCategory": "Vision Analysis Complete",
                "recommendations": [ai_response]
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )