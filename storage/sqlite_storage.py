import sqlite3
from typing import List, Dict
from storage.base import BaseStorage
import os


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str = "predictions.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prediction_sessions (
                    uid TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    original_image TEXT,
                    predicted_image TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS detection_objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_uid TEXT,
                    label TEXT,
                    score REAL,
                    box TEXT,
                    FOREIGN KEY (prediction_uid) REFERENCES prediction_sessions (uid)
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_prediction_uid ON detection_objects (prediction_uid)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_label ON detection_objects (label)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_score ON detection_objects (score)")

    def save_prediction(self, uid: str, original_image: str, predicted_image: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO prediction_sessions (uid, original_image, predicted_image)
                VALUES (?, ?, ?)
            """, (uid, original_image, predicted_image))

    def save_detection(self, prediction_uid: str, label: str, score: float, box: List[float]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO detection_objects (prediction_uid, label, score, box)
                VALUES (?, ?, ?, ?)
            """, (prediction_uid, label, score, str(box)))

    def get_prediction(self, uid: str) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            session = conn.execute("""
                SELECT * FROM prediction_sessions WHERE uid = ?
            """, (uid,)).fetchone()

            if not session:
                raise ValueError("Prediction not found")

            detections = conn.execute("""
                SELECT * FROM detection_objects WHERE prediction_uid = ?
            """, (uid,)).fetchall()

            return {
                "uid": session["uid"],
                "timestamp": session["timestamp"],
                "original_image": session["original_image"],
                "predicted_image": session["predicted_image"],
                "detection_objects": [
                    {
                        "id": row["id"],
                        "label": row["label"],
                        "score": row["score"],
                        "box": row["box"]
                    } for row in detections
                ]
            }

    def get_predictions_by_label(self, label: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT DISTINCT ps.uid, ps.timestamp
                FROM prediction_sessions ps
                JOIN detection_objects do ON ps.uid = do.prediction_uid
                WHERE do.label = ?
            """, (label,)).fetchall()

            return [{"uid": row["uid"], "timestamp": row["timestamp"]} for row in rows]

    def get_predictions_by_score(self, min_score: float) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT DISTINCT ps.uid, ps.timestamp
                FROM prediction_sessions ps
                JOIN detection_objects do ON ps.uid = do.prediction_uid
                WHERE do.score >= ?
            """, (min_score,)).fetchall()

            return [{"uid": row["uid"], "timestamp": row["timestamp"]} for row in rows]

    def get_prediction_image_path(self, uid: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT predicted_image FROM prediction_sessions WHERE uid = ?
            """, (uid,)).fetchone()

            if not row:
                raise ValueError("Prediction not found")
            return row[0]
