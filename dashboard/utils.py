"""
Dashboard Utilities - Data Loading and Helper Functions
"""
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path

# Base directory (parent of dashboard folder)
BASE = Path(__file__).parent.parent

def load_json(path):
    """Load JSON file"""
    with open(BASE / path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_pickle(path):
    """Load pickle file"""
    with open(BASE / path, "rb") as f:
        return pickle.load(f)

def load_student_features():
    """Load student features CSV"""
    return pd.read_csv(BASE / "models" / "features_all.csv")

def get_student_roadmap(student_id):
    """Get roadmap for specific student"""
    p = BASE / "roadmaps" / f"{student_id}_roadmap.json"
    if p.exists():
        return load_json(p)
    return None

def get_student_profile(student_id):
    """Get skill gap profile for student"""
    profiles = load_json("skill_gap_profiles/student_profiles.json")
    for profile in profiles:
        if profile.get('student_id') == student_id:
            return profile
    return None

def get_student_recommendations(student_id):
    """Get recommendations for student"""
    recs = load_json("recommendations/recommendations.json")
    for rec in recs:
        if rec.get('student_id') == student_id:
            return rec
    return None

def get_all_students():
    """Get list of all student IDs"""
    df = pd.read_csv(BASE / "digital_twin_students_1500_cleaned.csv", low_memory=False)
    return df['StudentID'].tolist()

def normalize_skills(skill_dict, max_val=100):
    """Normalize skill values to 0-1 range"""
    if not skill_dict:
        return {}
    values = list(skill_dict.values())
    if max(values) == 0:
        return {k: 0 for k in skill_dict}
    return {k: v/max_val for k, v in skill_dict.items()}

def get_career_color(career):
    """Get color for career category"""
    colors = {
        "Data": "#1f77b4",
        "Machine Learning": "#ff7f0e",
        "Cloud": "#2ca02c",
        "Cybersecurity": "#d62728",
        "Software": "#9467bd",
        "Network": "#8c564b",
        "DevOps": "#e377c2",
        "Other": "#7f7f7f"
    }
    return colors.get(career, "#7f7f7f")
