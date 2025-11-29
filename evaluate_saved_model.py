import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score

print("Loading artifacts...")
model = joblib.load("models/career_model_xgb.pkl")
le = joblib.load("models/label_encoder.pkl")
feature_cols = joblib.load("models/feature_list.pkl")
df_features = pd.read_csv("models/features_all.csv")

# Load original labels (we need to reconstruct the target variable y)
# We can get this from the features_all.csv if we saved it, but we only saved features.
# Wait, features_all.csv only has StudentID and features. We need the labels.
# Let's re-load the raw data to get labels, using the same logic as training.

print("Re-creating labels for evaluation...")
# We can't easily re-run the whole labeling logic without importing from train_career_model
# But we can try to import the labeling function or just re-implement the mapping quickly.
# Actually, let's just use the train_career_model.py logic to get the dataframe with labels again.

import sys
# We will just re-run the data loading and labeling part from train_career_model.py
# But that's heavy.
# Alternative: The model was trained on X and y.
# If I can't easily get y_test, I can't evaluate.
# Let's look at train_career_model.py again. It saves features_all.csv.
# Does features_all.csv contain the label?
# Line 259: features_all = df[['StudentID'] + feature_cols].copy()
# It does NOT contain the label.

# Okay, I need to re-generate the labels to evaluate.
# I will copy the label generation logic.

import json
import re
from pathlib import Path

BASE = Path(".")
df = pd.read_csv(BASE / "digital_twin_students_1500_cleaned.csv", low_memory=False)
with open(BASE / "skill_gap_profiles" / "student_profiles.json", "r") as f:
    profiles = json.load(f)

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

label_rows = []
profiles_map = {p['student_id']: p for p in profiles}
for sid in df['StudentID'].astype(str).tolist():
    p = profiles_map.get(sid, {})
    top_job = None
    if p.get("best_job_matches"):
        item = p["best_job_matches"][0]
        top_job = item.get("job_title") if isinstance(item, dict) else item
    label = map_job_to_class(top_job or "")
    label_rows.append({'StudentID': sid, 'career_label': label})

labels_df = pd.DataFrame(label_rows)
df = df.merge(labels_df, on="StudentID", how="left")

# Handle rare classes
class_counts = df['career_label'].value_counts()
rare_classes = class_counts[class_counts < 5].index.tolist()
if rare_classes:
    df.loc[df['career_label'].isin(rare_classes), 'career_label'] = 'Other'

# Prepare X and y
# We need to ensure X matches the model's expected features.
# We can load X from features_all.csv to be safe about feature engineering values
# but we need to merge with labels.

df_features = pd.read_csv("models/features_all.csv")
# Merge labels back to features
df_eval = df_features.merge(df[['StudentID', 'career_label']], on='StudentID')

X = df_eval[feature_cols]
y = le.transform(df_eval['career_label'])

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

print("\nEvaluating on Test Set...")
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='macro')

print(f"Accuracy: {acc:.4f}")
print(f"Macro F1: {f1:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))
