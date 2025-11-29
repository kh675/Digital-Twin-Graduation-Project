"""
FastAPI Backend for Digital Twin Dashboard
Provides REST API endpoints for student data access
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="Digital Twin API",
    description="API for student career prediction and roadmap generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory
BASE = Path(__file__).parent.parent

# Load models and data
models_dir = BASE / "models"
model = joblib.load(models_dir / "career_model_xgb.pkl")
le = joblib.load(models_dir / "label_encoder.pkl")
feature_cols = joblib.load(models_dir / "feature_list.pkl")

try:
    features_df = pd.read_csv(models_dir / "features_all.csv")
except Exception as e:
    print(f"Warning: Could not load features_all.csv: {e}")
    features_df = pd.DataFrame()

def read_json(path):
    """Read JSON file"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Digital Twin API",
        "version": "1.0.0",
        "endpoints": [
            "/predict-career/{student_id}",
            "/get-roadmap/{student_id}",
            "/get-recommendations/{student_id}",
            "/get-profile/{student_id}",
            "/health"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": model is not None}

@app.get("/predict-career/{student_id}")
def predict_career(student_id: str):
    """Predict career for a student"""
    row = features_df[features_df['StudentID'] == student_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    X = row[feature_cols].fillna(0)
    probs = model.predict_proba(X)[0]
    idx = int(probs.argmax())
    label = le.inverse_transform([idx])[0]
    
    # Create probability map
    prob_map = {cls: float(prob) for cls, prob in zip(le.classes_, probs)}
    
    return {
        "student_id": student_id,
        "predicted_career": label,
        "confidence": float(probs[idx]),
        "probabilities": prob_map
    }

@app.get("/get-roadmap/{student_id}")
def get_roadmap(student_id: str):
    """Get roadmap for a student"""
    p = BASE / "roadmaps" / f"{student_id}_roadmap.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Roadmap for {student_id} not found")
    return read_json(p)

@app.get("/get-recommendations/{student_id}")
def get_recommendations(student_id: str):
    """Get recommendations for a student"""
    p = BASE / "recommendations" / "recommendations.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="Recommendations file not found")
    
    recs = read_json(p)
    student_rec = next((x for x in recs if x.get('student_id') == student_id), None)
    
    if student_rec is None:
        raise HTTPException(status_code=404, detail=f"Recommendations for {student_id} not found")
    
    return student_rec

@app.get("/get-profile/{student_id}")
def get_profile(student_id: str):
    """Get skill gap profile for a student"""
    p = BASE / "skill_gap_profiles" / "student_profiles.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="Profiles file not found")
    
    profiles = read_json(p)
    student_profile = next((x for x in profiles if x.get('student_id') == student_id), None)
    
    if student_profile is None:
        raise HTTPException(status_code=404, detail=f"Profile for {student_id} not found")
    
    return student_profile

@app.get("/list-students")
def list_students(limit: int = 100):
    """List all student IDs"""
    try:
        df = pd.read_csv(BASE / "digital_twin_students_1500_cleaned.csv", low_memory=False)
        students = df['StudentID'].head(limit).tolist()
        return {"students": students, "total": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading students: {str(e)}")

@app.get("/cluster-student/{student_id}")
def get_student_cluster(student_id: str):
    """Get cluster information for a student"""
    try:
        # Load cluster assignments
        p = BASE / "cluster_assignments.json"
        if not p.exists():
            raise HTTPException(status_code=404, detail="Cluster data not found. Run clustering_engine.py first.")
        
        assignments = read_json(p)
        if student_id not in assignments:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found in clusters")
        
        assignment = assignments[student_id]
        
        # Load cluster members
        clusters = read_json(BASE / "clusters.json")
        cluster_label = assignment['cluster_label']
        cluster_members = clusters.get(cluster_label, [])
        
        # Load similar students
        similar = read_json(BASE / "similar_students.json")
        similar_students = similar.get(student_id, [])
        
        return {
            "student_id": student_id,
            "cluster_id": assignment['cluster_id'],
            "cluster_label": cluster_label,
            "cluster_size": len(cluster_members),
            "cluster_members": cluster_members[:10],  # First 10
            "similar_students": similar_students[:10]
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/cluster-profile/{cluster_label}")
def get_cluster_profile(cluster_label: str):
    """Get analytics for a specific cluster"""
    try:
        p = BASE / "cluster_profiles.json"
        if not p.exists():
            raise HTTPException(status_code=404, detail="Cluster profiles not found. Run clustering_engine.py first.")
        
        profiles = read_json(p)
        if cluster_label not in profiles:
            raise HTTPException(status_code=404, detail=f"Cluster {cluster_label} not found")
        
        return profiles[cluster_label]
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/similar-students/{student_id}")
def get_similar_students(student_id: str, limit: int = 10):
    """Get similar students based on feature similarity"""
    try:
        p = BASE / "similar_students.json"
        if not p.exists():
            raise HTTPException(status_code=404, detail="Similarity data not found. Run clustering_engine.py first.")
        
        similar = read_json(p)
        if student_id not in similar:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        similar_ids = similar[student_id][:limit]
        
        # Get basic info for similar students
        similar_info = []
        for sid in similar_ids:
            roadmap_path = BASE / "roadmaps" / f"{sid}_roadmap.json"
            if roadmap_path.exists():
                roadmap = read_json(roadmap_path)
                similar_info.append({
                    "student_id": sid,
                    "career_path": roadmap.get('career_path', 'Unknown')
                })
            else:
                similar_info.append({
                    "student_id": sid,
                    "career_path": "Unknown"
                })
        
        return {
            "student_id": student_id,
            "similar_students": similar_info
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/all-clusters")
def get_all_clusters():
    """Get overview of all clusters"""
    try:
        profiles = read_json(BASE / "cluster_profiles.json")
        clusters = read_json(BASE / "clusters.json")
        
        overview = []
        for label, profile in profiles.items():
            overview.append({
                "label": label,
                "cluster_id": profile['cluster_id'],
                "member_count": profile['member_count'],
                "avg_gpa": profile['avg_gpa'],
                "top_missing_skills": profile['top_missing_skills'][:5]
            })
        
        return {"clusters": overview, "total_clusters": len(overview)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Cluster data not found. Run clustering_engine.py first.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
