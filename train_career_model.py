"""
Step 4: Career Prediction Model - Production Training Script

This script trains a career prediction model and saves all artifacts.
Run this after completing the Jupyter notebook exploration.

Usage:
    python train_career_model.py

Outputs:
    models/career_model_xgb.pkl
    models/label_encoder.pkl
    models/emb_pca.pkl
    models/feature_list.pkl
    models/features_all.csv
"""

import os
import sys
import json
import pickle
import joblib
import re
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score

# Set encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set seeds
np.random.seed(42)

print("=" * 70)
print("STEP 4: CAREER PREDICTION MODEL - TRAINING")
print("=" * 70)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n1️⃣  Loading data...")

BASE = Path(".")
df = pd.read_csv(BASE / "digital_twin_students_1500_cleaned.csv", low_memory=False)
print(f"   Loaded {len(df)} students")

with open(BASE / "skill_gap_profiles" / "student_profiles.json", "r") as f:
    profiles = json.load(f)
print(f"   Loaded {len(profiles)} profiles")

with open(BASE / "embeddings" / "embeddings_students.pkl", "rb") as f:
    emb_data = pickle.load(f)
    student_ids = emb_data['ids']
    student_embeddings = np.vstack(emb_data['embeddings'])
print(f"   Loaded embeddings: {student_embeddings.shape}")

# ============================================================================
# 2. CREATE LABELS
# ============================================================================
print("\n2️⃣  Creating career labels...")

def map_job_to_class(job_title):
    """Map job title to career class with improved keywords"""
    t = str(job_title).lower()
    
    # Data
    if any(k in t for k in ["data analyst", "data engineer", "data scientist", "etl", "big data", "bi developer", "business intelligence", "tableau", "power bi", "sql developer"]):
        return "Data"
    # Machine Learning
    if any(k in t for k in ["machine learning", "ml", "deep learning", "ai", "artificial intelligence", "computer vision", "nlp", "data science"]):
        return "Machine Learning"
    # Cloud
    if any(k in t for k in ["cloud", "aws", "azure", "gcp", "kubernetes", "docker", "serverless"]):
        return "Cloud"
    # Cybersecurity
    if any(k in t for k in ["security", "cyber", "penetration", "infosec", "soc analyst", "ethical hacker"]):
        return "Cybersecurity"
    # Network
    if any(k in t for k in ["network", "routing", "switching", "cisco", "ccna", "ccnp"]):
        return "Network"
    # DevOps
    if any(k in t for k in ["devops", "sre", "site reliability", "ci/cd", "jenkins", "terraform", "ansible"]):
        return "DevOps"
    # Software
    if any(k in t for k in ["developer", "software", "backend", "frontend", "full stack", "engineer", "web", "react", "angular", "node", "java", "python", ".net"]):
        return "Software"
    
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

# Handle rare classes (less than 5 samples)
class_counts = df['career_label'].value_counts()
rare_classes = class_counts[class_counts < 5].index.tolist()
if rare_classes:
    print(f"   Warning: Found rare classes {rare_classes}. Mapping to 'Other'.")
    df.loc[df['career_label'].isin(rare_classes), 'career_label'] = 'Other'

print("   Label distribution:")
for label, count in df['career_label'].value_counts().items():
    print(f"     {label}: {count} ({count/len(df)*100:.1f}%)")

# ============================================================================
# 3. FEATURE ENGINEERING
# ============================================================================
print("\n3️⃣  Engineering features...")

# Academic features
df['GPA'] = pd.to_numeric(df['GPA'], errors='coerce').fillna(df['GPA'].mean())
df['AttendancePercent'] = pd.to_numeric(df.get('AttendancePercent', 0), errors='coerce').fillna(80)
df['FailedCourses'] = pd.to_numeric(df.get('FailedCourses', 0), errors='coerce').fillna(0)

# Skill and course counts
def list_count(cell):
    if pd.isna(cell): 
        return 0
    s = str(cell).strip()
    if s == "" or s.lower() == "nan": 
        return 0
    return len([x for x in re.split(r'[;,|/]+', s) if x.strip()])

df['num_skills'] = df.get('Skills', "").apply(list_count)
df['num_courses_completed'] = df.get('CoursesCompleted', "").apply(list_count)

# NEW FEATURES: Project and Internship counts
df['project_count'] = df.get('Projects', "").apply(list_count)
df['internship_count'] = df.get('Internships', "").apply(list_count)

# Major average - use GPA since grade columns contain letters not numbers
df['major_avg'] = df['GPA']

# Gap features
def get_profile(sid):
    return profiles_map.get(str(sid), {})

df['num_missing_skills'] = df['StudentID'].apply(
    lambda s: len(get_profile(s).get('skill_gaps', {}).get('missing_skills', []))
)

def top_priority_mean(sid):
    arr = get_profile(sid).get('skill_gaps', {}).get('priority_skills', [])
    if not arr: 
        return 0.0
    vals = [x.get('priority_score', 0) for x in arr]
    return float(np.mean(vals))

df['top_missing_priority'] = df['StudentID'].apply(top_priority_mean)

# Embedding PCA
emb_map = {str(sid): emb for sid, emb in zip(student_ids, student_embeddings)}
emb_matrix = np.vstack([
    emb_map.get(str(sid), np.zeros(student_embeddings.shape[1])) 
    for sid in df['StudentID']
])

# Use min of 32 or available dimensions
n_components = min(32, emb_matrix.shape[1], emb_matrix.shape[0] - 1)
pca = PCA(n_components=n_components, random_state=42)
emb_pca = pca.fit_transform(emb_matrix)
print(f"   PCA explained variance: {pca.explained_variance_ratio_.sum():.3f}")

for i in range(emb_pca.shape[1]):
    df[f'emb_pca_{i}'] = emb_pca[:, i]

print(f"   Total features: {8 + emb_pca.shape[1]} (8 academic/gap + {emb_pca.shape[1]} embedding)")

# ============================================================================
# 4. PREPARE DATA
# ============================================================================
print("\n4️⃣  Preparing data for training...")

feature_cols = [
    'GPA', 'major_avg', 'AttendancePercent', 'FailedCourses',
    'num_skills', 'num_courses_completed', 'project_count', 'internship_count',
    'num_missing_skills', 'top_missing_priority'
] + [c for c in df.columns if c.startswith('emb_pca_')]

X = df[feature_cols].fillna(0)
le = LabelEncoder()
y = le.fit_transform(df['career_label'].fillna('Other'))

print(f"   Feature matrix: {X.shape}")
print(f"   Classes: {list(le.classes_)}")

# Verify data quality
assert not np.any(np.isnan(X.values)), "Found NaN values!"
assert np.isfinite(X.values).all(), "Found inf values!"

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"   Train: {len(X_train)}, Test: {len(X_test)}")

# ============================================================================
# 5. TRAIN MODEL
# ============================================================================
print("\n5️⃣  Training XGBoost model...")

xgb = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=1
)

xgb.fit(X_train, y_train)

# ============================================================================
# 6. EVALUATE
# ============================================================================
print("\n6️⃣  Evaluating model...")

yhat = xgb.predict(X_test)
acc = accuracy_score(y_test, yhat)
f1 = f1_score(y_test, yhat, average='macro')

print(f"   Accuracy: {acc:.3f}")
print(f"   Macro F1: {f1:.3f}")

print("\n   Classification Report:")
print(classification_report(y_test, yhat, target_names=le.classes_))

# Cross-validation
print("\n   Running 5-fold cross-validation...")
cv_scores = cross_val_score(xgb, X, y, cv=5, scoring='f1_macro', n_jobs=-1)
print(f"   CV F1: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

# ============================================================================
# 7. SAVE ARTIFACTS
# ============================================================================
print("\n7️⃣  Saving artifacts...")

os.makedirs("models", exist_ok=True)

joblib.dump(xgb, "models/career_model_xgb.pkl")
joblib.dump(le, "models/label_encoder.pkl")
joblib.dump(pca, "models/emb_pca.pkl")
joblib.dump(feature_cols, "models/feature_list.pkl")

# Save feature matrix for API
features_all = df[['StudentID'] + feature_cols].copy()
features_all.to_csv("models/features_all.csv", index=False)

# Save feature importance
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': xgb.feature_importances_
}).sort_values('importance', ascending=False)
feature_importance.to_csv("models/feature_importance.csv", index=False)

print("   ✅ Saved:")
print("      - career_model_xgb.pkl")
print("      - label_encoder.pkl")
print("      - emb_pca.pkl")
print("      - feature_list.pkl")
print("      - features_all.csv")
print("      - feature_importance.csv")

# ============================================================================
# 8. TEST PREDICTION
# ============================================================================
print("\n8️⃣  Testing prediction function...")

def predict_career(student_id):
    """Predict career for a single student"""
    row = df[df['StudentID'] == str(student_id)]
    if row.shape[0] == 0:
        return {"student_id": student_id, "error": "student not found"}
    
    X_row = row[feature_cols].fillna(0)
    probs = xgb.predict_proba(X_row)[0]
    idx = np.argmax(probs)
    label = le.inverse_transform([idx])[0]
    
    top3_idx = probs.argsort()[-3:][::-1]
    top3 = [le.inverse_transform([i])[0] for i in top3_idx]
    
    return {
        "student_id": student_id,
        "predicted_career": label,
        "confidence": float(probs[idx]),
        "top_3_careers": top3
    }

# Test on sample students
sample_ids = df['StudentID'].sample(3, random_state=42).tolist()
for sid in sample_ids:
    result = predict_career(sid)
    print(f"   {sid}: {result['predicted_career']} ({result['confidence']:.2%})")

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETE!")
print(f"   Macro F1: {f1:.3f}")
print(f"   Model saved to: models/career_model_xgb.pkl")
print("=" * 70)
