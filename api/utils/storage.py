# api/utils/storage.py
import os
import json
import csv
from datetime import datetime
from typing import Dict

DATA_DIR = os.environ.get("DATA_DIR", "./data")
PDF_DIR = os.environ.get("PDF_OUTPUT_DIR", "./pdf_reports")
STUDENT_JSON_DIR = os.path.join(DATA_DIR, "student_inputs")
os.makedirs(STUDENT_JSON_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, "student_inputs.csv")

def next_student_id() -> str:
    """Create a new sequential student id S1501 etc based on existing csv or json."""
    # Simple logic: if csv exists, use count+1, else start S1501
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
            count = max(0, len(rows)-1)  # minus header
            return f"S{count+1501:04d}"
    # fallback
    return "S1501"

def save_student_json(student_id: str, payload: Dict):
    path = os.path.join(STUDENT_JSON_DIR, f"{student_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path

def append_student_csv(student_id: str, payload: Dict):
    header = ["student_id","name","email","department","level","gpa","created_at"]
    row = [
        student_id,
        payload.get("name",""),
        payload.get("email",""),
        payload.get("department",""),
        str(payload.get("academic_level","")),
        str(payload.get("gpa","")),
        datetime.utcnow().isoformat()
    ]
    exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(header)
        writer.writerow(row)
    return CSV_FILE

def get_student_json(student_id: str) -> Dict:
    """Retrieve student data from JSON file."""
    path = os.path.join(STUDENT_JSON_DIR, f"{student_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
