"""
SQLite database for the Color Vision app.

Flow (easy to remember):
  1. Frontend sends JSON to Flask (flask_app.py)
  2. Flask calls a function here (e.g. save_test_result)
  3. We run SQL (INSERT / SELECT / DELETE)
  4. Data is stored in the file: backend/data/eyevision.db
"""

import json
import os
import sqlite3
from pathlib import Path

# Path to the .db file (one file = whole database)
DB_PATH = os.getenv("DATABASE_PATH")
# If the environment variable points to a location inside the container's read‑only root (e.g., "/app"), fall back to the local data folder.
if not DB_PATH or DB_PATH.startswith("/app"):
    DB_PATH = str(Path(__file__).parent / "data" / "eyevision.db")


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_db():
    """Open a connection to the SQLite file. Creates the data folder if needed, without trying to create the root directory."""
    # Determine the directory for the DB file
    dir_path = os.path.dirname(DB_PATH)
    # Do not attempt to create the container root or any path under '/app' (read‑only in Docker)
    if dir_path and not dir_path.startswith("/app") and not os.path.isdir(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts: row["score"]
    return conn


def create_tables():
    """
    Create all tables if they do not exist yet.
    Called once when the server starts.
    """
    conn = get_db()
    cursor = conn.cursor()

    # --- Table: test_results (main table for Ishihara, Tritan, Hue, Webcam, Amsler) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL DEFAULT 'anonymous',
            test_type TEXT NOT NULL,
            score REAL NOT NULL DEFAULT 0,
            diagnosis TEXT NOT NULL DEFAULT '',
            total_questions INTEGER NOT NULL DEFAULT 0,
            correct_answers INTEGER NOT NULL DEFAULT 0,
            test_data TEXT NOT NULL DEFAULT '{}',
            difficulty TEXT NOT NULL DEFAULT 'standard',
            duration_seconds INTEGER NOT NULL DEFAULT 0,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Small helpers (JSON in test_data column)
# ---------------------------------------------------------------------------

def to_json(data):
    """Turn a Python dict/list into a string for the database."""
    return json.dumps(data if data is not None else {})


def from_json(text):
    """Turn a database string back into a Python dict."""
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def row_to_dict(row):
    """Convert one test_results row to JSON-friendly dict for the frontend."""
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "userId": row["user_id"],
        "test_type": row["test_type"],
        "testType": row["test_type"],
        "score": row["score"],
        "diagnosis": row["diagnosis"],
        "result": row["diagnosis"],
        "total_questions": row["total_questions"],
        "totalQuestions": row["total_questions"],
        "correct_answers": row["correct_answers"],
        "correctAnswers": row["correct_answers"],
        "test_data": from_json(row["test_data"]),
        "testData": from_json(row["test_data"]),
        "difficulty": row["difficulty"],
        "duration_seconds": row["duration_seconds"],
        "durationSeconds": row["duration_seconds"],
        "timestamp": row["timestamp"],
    }


# ---------------------------------------------------------------------------
# TEST RESULTS — save / read / delete
# ---------------------------------------------------------------------------

def save_test_result(
    result_id,
    user_id,
    test_type,
    score,
    diagnosis,
    total_questions,
    correct_answers,
    test_data,
    difficulty,
    duration_seconds,
    timestamp,
):
    """
    INSERT one test result into the database.

    Example test_type values: 'ishihara', 'tritan', 'hue', 'webcam', 'amsler'
    """
    conn = get_db()
    conn.execute(
        """
        INSERT INTO test_results (
            id, user_id, test_type, score, diagnosis,
            total_questions, correct_answers, test_data,
            difficulty, duration_seconds, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result_id,
            user_id,
            test_type,
            score,
            diagnosis,
            total_questions,
            correct_answers,
            to_json(test_data),
            difficulty,
            duration_seconds,
            timestamp,
        ),
    )
    conn.commit()
    conn.close()


def get_test_results(user_id=None, test_type=None, limit=50, offset=0):
    """
    SELECT test results from the database.
    Newest first.
    """
    conn = get_db()

    sql = "SELECT * FROM test_results WHERE 1=1"
    params = []

    if user_id and user_id != "anonymous":
        sql += " AND user_id = ?"
        params.append(user_id)

    if test_type:
        sql += " AND test_type = ?"
        params.append(test_type)

    sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.append(limit)
    params.append(offset)

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return [row_to_dict(row) for row in rows]


def count_test_results(user_id=None, test_type=None):
    """How many rows match (for pagination)."""
    conn = get_db()

    sql = "SELECT COUNT(*) FROM test_results WHERE 1=1"
    params = []

    if user_id and user_id != "anonymous":
        sql += " AND user_id = ?"
        params.append(user_id)

    if test_type:
        sql += " AND test_type = ?"
        params.append(test_type)

    total = conn.execute(sql, params).fetchone()[0]
    conn.close()
    return total


def delete_test_result(result_id):
    """DELETE one result by id. Returns True if something was deleted."""
    conn = get_db()
    cursor = conn.execute("DELETE FROM test_results WHERE id = ?", (result_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def clear_test_results(user_id=None):
    """DELETE many results. If user_id is set, only that user's rows."""
    conn = get_db()

    if user_id and user_id != "anonymous":
        cursor = conn.execute("DELETE FROM test_results WHERE user_id = ?", (user_id,))
    else:
        cursor = conn.execute("DELETE FROM test_results")

    conn.commit()
    deleted_count = cursor.rowcount
    conn.close()
    return deleted_count


def get_test_stats():
    """Count how many tests exist for each test_type."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM test_results").fetchone()[0]

    def count_type(name):
        return conn.execute(
            "SELECT COUNT(*) FROM test_results WHERE test_type = ?", (name,)
        ).fetchone()[0]

    stats = {
        "total_results": total,
        "ishihara_count": count_type("ishihara"),
        "tritan_count": count_type("tritan"),
        "hue_count": count_type("hue"),
        "webcam_count": count_type("webcam"),
        "amsler_count": count_type("amsler"),
        "contrast_count": count_type("contrast"),
    }
    conn.close()
    return stats


def count_users():
    return 0
