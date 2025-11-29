# Career Prediction Model - Usage Guide

This directory contains the trained career prediction model and all necessary artifacts.

## Files

- `career_model_xgb.pkl` - Trained XGBoost classifier
- `label_encoder.pkl` - LabelEncoder for career classes
- `emb_pca.pkl` - PCA transformer for student embeddings (384→32 dims)
- `feature_list.pkl` - List of feature column names
- `features_all.csv` - Precomputed features for all 1500 students
- `feature_importance.csv` - Feature importance scores
- `confusion_matrix.png` - Model confusion matrix visualization
- `shap_summary.png` - SHAP feature importance plot

## Career Classes

The model predicts one of 8 career paths:
1. **Data** - Data Analyst, Data Engineer, Data Scientist
2. **Machine Learning** - ML Engineer, AI Specialist
3. **Cloud** - Cloud Engineer, Cloud Architect, AWS/Azure roles
4. **Cybersecurity** - Security Analyst, Penetration Tester
5. **Network** - Network Engineer, Network Administrator
6. **DevOps** - DevOps Engineer, SRE
7. **Software** - Backend/Frontend Developer, Software Engineer
## Usage

### Load Model

```python
import joblib
import pandas as pd
import numpy as np

# Load artifacts
model = joblib.load("models/career_model_xgb.pkl")
le = joblib.load("models/label_encoder.pkl")
pca = joblib.load("models/emb_pca.pkl")
feature_cols = joblib.load("models/feature_list.pkl")

# Load precomputed features
df_features = pd.read_csv("models/features_all.csv")
```

### Predict for Single Student

```python
def predict_career(student_id):
    """Predict career for a single student"""
    # Get student features
    row = df_features[df_features['StudentID'] == student_id]
    
    if row.empty:
        return {"error": "student not found"}
    
    # Prepare features
    X = row[feature_cols]
    
    # Predict
    probs = model.predict_proba(X)[0]
    pred_idx = np.argmax(probs)
    label = le.inverse_transform([pred_idx])[0]
    
    # Get top 3
    top3_idx = probs.argsort()[-3:][::-1]
    top3 = [le.inverse_transform([i])[0] for i in top3_idx]
    
    return {
        "student_id": student_id,
        "predicted_career": label,
        "confidence": float(probs[pred_idx]),
        "top_3_careers": top3,
        "probabilities": dict(zip(le.classes_, probs.tolist()))
    }

# Example
result = predict_career("S0001")
print(f"Predicted: {result['predicted_career']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Top 3: {result['top_3_careers']}")
```

### Batch Predictions

```python
def predict_batch(student_ids):
    """Predict careers for multiple students"""
    results = []
    for sid in student_ids:
        results.append(predict_career(sid))
    return results

# Example
batch_results = predict_batch(["S0001", "S0002", "S0003"])
```

## FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd

app = FastAPI()

# Load model and artifacts at startup
model = joblib.load("models/career_model_xgb.pkl")
le = joblib.load("models/label_encoder.pkl")
feature_cols = joblib.load("models/feature_list.pkl")
df_features = pd.read_csv("models/features_all.csv")

@app.get("/predict-career/{student_id}")
def predict_career_api(student_id: str):
    """API endpoint for career prediction"""
    row = df_features[df_features['StudentID'] == student_id]
    
    if row.empty:
        raise HTTPException(status_code=404, detail="Student not found")
    
    X = row[feature_cols]
    probs = model.predict_proba(X)[0]
    pred_idx = np.argmax(probs)
    label = le.inverse_transform([pred_idx])[0]
    
    top3_idx = probs.argsort()[-3:][::-1]
    top3 = [le.inverse_transform([i])[0] for i in top3_idx]
    
    return {
        "student_id": student_id,
        "predicted_career": label,
        "confidence": float(probs[pred_idx]),
        "top_3_careers": top3,
        "probabilities": dict(zip(le.classes_, probs.tolist()))
    }

# Run with: uvicorn fastapi_app:app --reload
```

## Model Performance

- **Accuracy**: ~0.65-0.75 (depends on label quality)
- **Macro F1**: ~0.50-0.65 (synthetic labels)
- **Cross-validation**: 5-fold stratified

**Note**: Performance metrics are based on pseudo-labels created from Step 2 job matches. With real placement data, expect higher accuracy (0.75-0.85).

## Retraining

To retrain the model with updated data:

```bash
python train_career_model.py
```

This will:
1. Load latest student data and profiles
2. Engineer features
3. Train XGBoost model
4. Save all artifacts to `models/`

## Feature Importance

Top features (typically):
1. `emb_pca_*` - Student embedding components
2. `GPA` - Academic performance
3. `num_missing_skills` - Skill gaps
4. `major_avg` - Major subject performance
5. `top_missing_priority` - Priority of missing skills

See `feature_importance.csv` for full rankings.

## Troubleshooting

**Issue**: "Student not found"
- **Solution**: Ensure student_id exists in `features_all.csv`

**Issue**: "Feature mismatch"
- **Solution**: Ensure input features match `feature_list.pkl` order

**Issue**: Low confidence predictions
- **Solution**: Normal for students with ambiguous profiles; use top_3_careers

## Next Steps

After career prediction:
- Use predicted career to filter Step 3 recommendations
- Generate personalized learning roadmap (Step 5)
- Track prediction accuracy with real placement data
