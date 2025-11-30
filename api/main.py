"""
FastAPI Backend for Digital Twin Dashboard
Provides REST API endpoints for student data access
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Dict, Any
import json
import joblib
import pandas as pd
import numpy as np
import traceback
import os

# Import StudentForm model for digital twin creation
from api.models.student_form_model import StudentForm

# Import pipeline and utilities for Step 12
from api.dt_pipeline.student_pipeline import run_student_pipeline
from api.utils.storage import next_student_id, save_student_json, append_student_csv, get_student_json
from api.utils.pdf_wrapper import generate_student_pdf

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

# ============================================================================
# STEP 12: CREATE DIGITAL TWIN ENDPOINT
# ============================================================================

@app.post("/create_digital_twin", summary="Create student digital twin")
def create_digital_twin(form: StudentForm) -> Dict[str, Any]:
    """
    Full pipeline endpoint.
    Validates input, runs pipeline, saves outputs, generates PDF and returns summary.
    """
    try:
        # 1) assign ID
        student_payload = form.dict()
        student_id = next_student_id()

        # include id and metadata
        student_payload["student_id"] = student_id

        # 2) run pipeline (returns digital_twin dict)
        digital_twin = run_student_pipeline(student_payload)

        # 3) save student raw input and append csv
        save_student_json(student_id, student_payload)
        append_student_csv(student_id, student_payload)

        # 4) generate PDF (synchronous for demo)
        pdf_path = generate_student_pdf(student_id, digital_twin)
        # convert to URL path for dashboard assuming static serving from /pdf_reports
        pdf_url = os.path.join("/pdf_reports", os.path.basename(pdf_path))

        # 5) add links and metadata to result
        result = {
            "student_id": student_id,
            "digital_twin": digital_twin,
            "pdf_path": pdf_path,
            "pdf_url": pdf_url,
            "dashboard_url": f"{os.environ.get('DASHBOARD_BASE','http://localhost:8501')}/?student={student_id}"
        }
        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

@app.get("/get_digital_twin/{student_id}", summary="Get student digital twin")
def get_digital_twin(student_id: str) -> Dict[str, Any]:
    """
    Retrieve an existing digital twin by Student ID.
    """
    data = get_student_json(student_id)
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # We need to return the same structure as the POST endpoint expects for the dashboard
    # The saved JSON is the student payload which might NOT include the generated digital twin output 
    # if we only saved the input payload in save_student_json.
    # Let's check save_student_json implementation.
    # It saves 'student_payload'. In create_digital_twin, 'student_payload' is form.dict() + student_id.
    # It DOES NOT include the 'digital_twin' result from the pipeline.
    # So we need to RE-RUN the pipeline or save the result.
    # Re-running is safer for now to ensure we have the latest logic.
    
    try:
        # Re-run pipeline to get digital twin data
        digital_twin = run_student_pipeline(data)
        
        return {
            "student_id": student_id,
            "digital_twin": digital_twin,
            "input_summary": data
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error regenerating twin: {str(e)}")


# Mount static files for PDF serving
PDF_DIR = os.environ.get("PDF_OUTPUT_DIR", "./pdf_reports")
if os.path.exists(PDF_DIR):
    app.mount("/pdf_reports", StaticFiles(directory=PDF_DIR), name="pdf_reports")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
