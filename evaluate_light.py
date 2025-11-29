import pandas as pd
import joblib
import numpy as np
import json
from sklearn.metrics import accuracy_score, f1_score, classification_report
from pathlib import Path

print("Loading artifacts...")
model = joblib.load("models/career_model_xgb.pkl")
le = joblib.load("models/label_encoder.pkl")
feature_cols = joblib.load("models/feature_list.pkl")
df_features = pd.read_csv("models/features_all.csv")

print("Loading profiles (subset)...")
BASE = Path(".")
# Load profiles
with open(BASE / "skill_gap_profiles" / "student_profiles.json", "r") as f:
    profiles = json.load(f)

# Create labels for ALL students (it's fast enough in memory usually, the issue might be the CSV reading of the big file)
# We don't need the big CSV if we have profiles and features_all.csv (which has StudentID)

def map_job_to_class(job_title):
    t = str(job_title).lower()
    if any(k in t for k in ["data analyst", "data engineer", "data scientist", "etl", "big data", "bi developer", "business intelligence", "tableau", "power bi", "sql developer"]): return "Data"
    if any(k in t for k in ["machine learning", "ml", "deep learning", "ai", "artificial intelligence", "computer vision", "nlp", "data science"]): return "Machine Learning"
    if any(k in t for k in ["cloud", "aws", "azure", "gcp", "kubernetes", "docker", "serverless"]): return "Cloud"
    if any(k in t for k in ["security", "cyber", "penetration", "infosec", "soc analyst", "ethical hacker"]): return "Cybersecurity"
    if any(k in t for k in ["network", "routing", "switching", "cisco", "ccna", "ccnp"]): return "Network"
    if any(k in t for k in ["devops", "sre", "site reliability", "ci/cd", "jenkins", "terraform", "ansible"]): return "DevOps"
    if any(k in t for k in ["developer", "software", "backend", "frontend", "full stack", "engineer", "web", "react", "angular", "node", "java", "python", ".net"]): return "Software"
    return "Other"

print("Generating labels...")
label_map = {}
for p in profiles:
    sid = p['student_id']
    top_job = None
    if p.get("best_job_matches"):
        item = p["best_job_matches"][0]
        top_job = item.get("job_title") if isinstance(item, dict) else item
    label_map[sid] = map_job_to_class(top_job or "")

# Merge labels
df_features['career_label'] = df_features['StudentID'].map(label_map)

# Handle rare classes (same logic as training)
class_counts = df_features['career_label'].value_counts()
rare_classes = class_counts[class_counts < 5].index.tolist()
if rare_classes:
    df_features.loc[df_features['career_label'].isin(rare_classes), 'career_label'] = 'Other'

# Prepare Data
X = df_features[feature_cols]
y_true = le.transform(df_features['career_label'])

print("Predicting...")
y_pred = model.predict(X)

acc = accuracy_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred, average='macro')

print(f"METRICS_START")
print(f"Accuracy: {acc:.4f}")
print(f"Macro F1: {f1:.4f}")
print(f"METRICS_END")

print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=le.classes_))
