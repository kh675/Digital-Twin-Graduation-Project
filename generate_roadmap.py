"""
Step 5: Personalized Roadmap Generator - Production Script

This script generates 3-stage learning roadmaps for all 1500 students.
It integrates data from:
- Step 2: Skill Gap Profiles
- Step 3: Recommendations
- Step 4: Career Prediction Model

Output:
- roadmaps/Sxxxx_roadmap.json for each student
"""

import pandas as pd
import numpy as np
import json
import joblib
import os
import sys
from pathlib import Path
from tqdm import tqdm

# Set encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=" * 70)
print("STEP 5: PERSONALIZED ROADMAP GENERATOR")
print("=" * 70)

# ============================================================================
# 0. CONFIGURATION & TEMPLATES
# ============================================================================

BASE_DIR = Path(".")
MODELS_DIR = BASE_DIR / "models"
PROFILES_DIR = BASE_DIR / "skill_gap_profiles"
RECS_DIR = BASE_DIR / "recommendations"
ROADMAPS_DIR = BASE_DIR / "roadmaps"

PROJECT_TEMPLATES = {
    "Data": {
        "Beginner": {"title": "Exploratory Data Analysis on Titanic Dataset", "skills": ["python", "pandas", "matplotlib"], "type": "Analysis", "difficulty": "Beginner"},
        "Intermediate": {"title": "E-commerce Sales Dashboard", "skills": ["sql", "tableau", "data cleaning"], "type": "Visualization", "difficulty": "Intermediate"},
        "Advanced": {"title": "Predictive Customer Churn Model", "skills": ["scikit-learn", "feature engineering", "modeling"], "type": "ML", "difficulty": "Advanced"}
    },
    "Machine Learning": {
        "Beginner": {"title": "House Price Prediction", "skills": ["python", "regression", "scikit-learn"], "type": "Regression", "difficulty": "Beginner"},
        "Intermediate": {"title": "Image Classification with CNNs", "skills": ["tensorflow", "deep learning", "cnn"], "type": "Computer Vision", "difficulty": "Intermediate"},
        "Advanced": {"title": "End-to-End NLP Chatbot", "skills": ["nlp", "transformers", "deployment"], "type": "NLP", "difficulty": "Advanced"}
    },
    "Cloud": {
        "Beginner": {"title": "Static Website Hosting on AWS S3", "skills": ["aws", "s3", "dns"], "type": "Infrastructure", "difficulty": "Beginner"},
        "Intermediate": {"title": "Serverless API with Lambda & DynamoDB", "skills": ["aws lambda", "api gateway", "nosql"], "type": "Backend", "difficulty": "Intermediate"},
        "Advanced": {"title": "Multi-Tier Microservices Architecture", "skills": ["kubernetes", "docker", "terraform"], "type": "DevOps", "difficulty": "Advanced"}
    },
    "Cybersecurity": {
        "Beginner": {"title": "Network Traffic Analysis with Wireshark", "skills": ["networking", "wireshark", "protocols"], "type": "Analysis", "difficulty": "Beginner"},
        "Intermediate": {"title": "Vulnerability Scanner Implementation", "skills": ["python", "security", "scripting"], "type": "Security Tool", "difficulty": "Intermediate"},
        "Advanced": {"title": "Simulated Penetration Test Report", "skills": ["metasploit", "ethical hacking", "reporting"], "type": "PenTesting", "difficulty": "Advanced"}
    },
    "Software": {
        "Beginner": {"title": "Personal Portfolio Website", "skills": ["html", "css", "javascript"], "type": "Frontend", "difficulty": "Beginner"},
        "Intermediate": {"title": "REST API for Task Management", "skills": ["nodejs", "express", "mongodb"], "type": "Backend", "difficulty": "Intermediate"},
        "Advanced": {"title": "Full Stack E-commerce Platform", "skills": ["react", "redux", "stripe integration"], "type": "Full Stack", "difficulty": "Advanced"}
    },
    "Network": {
        "Beginner": {"title": "Home Network Setup & Configuration", "skills": ["networking", "routers", "ip addressing"], "type": "Setup", "difficulty": "Beginner"},
        "Intermediate": {"title": "Cisco Packet Tracer Simulation", "skills": ["cisco", "routing", "switching"], "type": "Simulation", "difficulty": "Intermediate"},
        "Advanced": {"title": "Network Automation with Python", "skills": ["python", "ansible", "network automation"], "type": "Automation", "difficulty": "Advanced"}
    },
    "DevOps": {
        "Beginner": {"title": "Dockerizing a Web Application", "skills": ["docker", "containers", "linux"], "type": "Containerization", "difficulty": "Beginner"},
        "Intermediate": {"title": "CI/CD Pipeline with Jenkins", "skills": ["jenkins", "git", "automation"], "type": "CI/CD", "difficulty": "Intermediate"},
        "Advanced": {"title": "Infrastructure as Code with Terraform", "skills": ["terraform", "aws", "iac"], "type": "IaC", "difficulty": "Advanced"}
    }
}

CERT_PATHS = {
    "Cloud": ["AWS Cloud Practitioner", "AWS Solutions Architect Associate", "Huawei HCIA Cloud"],
    "Data": ["Google Data Analytics", "Azure Data Scientist Associate", "IBM Data Science"],
    "Machine Learning": ["TensorFlow Developer Certificate", "AWS Machine Learning Specialty", "DeepLearning.AI"],
    "Cybersecurity": ["CompTIA Security+", "Certified Ethical Hacker (CEH)", "CISSP"],
    "Network": ["Cisco CCNA", "Cisco CCNP", "Huawei HCIA Datacom"],
    "DevOps": ["Docker Certified Associate", "CKA (Kubernetes Administrator)", "AWS DevOps Engineer"],
    "Software": ["Oracle Java Associate", "Meta Front-End Developer", "AWS Developer Associate"]
}

# ============================================================================
# 1. VALIDATION
# ============================================================================

def validate_environment():
    print("\n1️⃣  Validating environment...")
    required_files = [
        BASE_DIR / "digital_twin_students_1500_cleaned.csv",
        PROFILES_DIR / "student_profiles.json",
        RECS_DIR / "recommendations.json",
        MODELS_DIR / "career_model_xgb.pkl",
        MODELS_DIR / "label_encoder.pkl",
        MODELS_DIR / "feature_list.pkl",
        MODELS_DIR / "features_all.csv"
    ]
    
    missing = []
    for f in required_files:
        if not f.exists():
            missing.append(str(f))
            
    if missing:
        print("❌ CRITICAL ERROR: Missing required files:")
        for m in missing:
            print(f"   - {m}")
        sys.exit(1)
        
    os.makedirs(ROADMAPS_DIR, exist_ok=True)
    print("✅ All required files found.")

# ============================================================================
# 2. DATA LOADING
# ============================================================================

def load_data():
    print("\n2️⃣  Loading data...")
    
    # Students
    df_students = pd.read_csv(BASE_DIR / "digital_twin_students_1500_cleaned.csv", low_memory=False)
    print(f"   Loaded {len(df_students)} students")
    
    # Profiles
    with open(PROFILES_DIR / "student_profiles.json", "r") as f:
        profiles = json.load(f)
    profiles_map = {p['student_id']: p for p in profiles}
    print(f"   Loaded {len(profiles)} profiles")
    
    # Recommendations
    with open(RECS_DIR / "recommendations.json", "r") as f:
        recommendations = json.load(f)
    recs_map = {r['student_id']: r for r in recommendations}
    print(f"   Loaded {len(recommendations)} recommendations")
    
    # Models
    print("   Loading career models...")
    model = joblib.load(MODELS_DIR / "career_model_xgb.pkl")
    le = joblib.load(MODELS_DIR / "label_encoder.pkl")
    feature_cols = joblib.load(MODELS_DIR / "feature_list.pkl")
    df_features = pd.read_csv(MODELS_DIR / "features_all.csv")
    
    return df_students, profiles_map, recs_map, model, le, feature_cols, df_features

# ============================================================================
# 3. CORE LOGIC
# ============================================================================

def map_job_to_class(job_title):
    """Map job title to career class"""
    t = str(job_title).lower()
    if any(k in t for k in ["data analyst", "data engineer", "data scientist", "etl", "big data", "bi developer", "business intelligence", "tableau", "power bi", "sql developer"]): return "Data"
    if any(k in t for k in ["machine learning", "ml", "deep learning", "ai", "artificial intelligence", "computer vision", "nlp", "data science"]): return "Machine Learning"
    if any(k in t for k in ["cloud", "aws", "azure", "gcp", "kubernetes", "docker", "serverless"]): return "Cloud"
    if any(k in t for k in ["security", "cyber", "penetration", "infosec", "soc analyst", "ethical hacker"]): return "Cybersecurity"
    if any(k in t for k in ["network", "routing", "switching", "cisco", "ccna", "ccnp"]): return "Network"
    if any(k in t for k in ["devops", "sre", "site reliability", "ci/cd", "jenkins", "terraform", "ansible"]): return "DevOps"
    if any(k in t for k in ["developer", "software", "backend", "frontend", "full stack", "engineer", "web", "react", "angular", "node", "java", "python", ".net"]): return "Software"
    return "Other"

def get_predicted_career(student_id, df_features, model, le, feature_cols):
    """Get predicted career from Step 4 model"""
    row = df_features[df_features['StudentID'] == student_id]
    if row.empty:
        return None, 0.0
    
    X = row[feature_cols]
    probs = model.predict_proba(X)[0]
    idx = np.argmax(probs)
    label = le.inverse_transform([idx])[0]
    confidence = probs[idx]
    return label, confidence

def determine_career_path(student_id, profiles_map, df_features, model, le, feature_cols):
    """Determine best career path using multiple signals"""
    # 1. Prediction
    pred_label, conf = get_predicted_career(student_id, df_features, model, le, feature_cols)
    
    # If high confidence and not 'Other', use it
    if pred_label and pred_label != "Other" and conf > 0.4:
        return pred_label, "Prediction"
    
    # 2. Target Job from Step 2
    profile = profiles_map.get(student_id, {})
    if profile.get("best_job_matches"):
        item = profile["best_job_matches"][0]
        job_title = item.get("job_title") if isinstance(item, dict) else item
        mapped_label = map_job_to_class(job_title)
        if mapped_label != "Other":
            return mapped_label, "Target Job"
            
    # 3. Fallback
    return pred_label if pred_label else "Software", "Fallback"

def get_project_template(career, stage):
    """Get project template for career and stage"""
    cat = career if career in PROJECT_TEMPLATES else "Software"
    return PROJECT_TEMPLATES[cat].get(stage, PROJECT_TEMPLATES["Software"][stage])

# ============================================================================
# 4. MAIN GENERATION LOOP
# ============================================================================

def main():
    validate_environment()
    df_students, profiles_map, recs_map, model, le, feature_cols, df_features = load_data()
    
    print("\n3️⃣  Generating roadmaps...")
    
    generated_count = 0
    for student_id in tqdm(df_students['StudentID']):
        career, source = determine_career_path(student_id, profiles_map, df_features, model, le, feature_cols)
        profile = profiles_map.get(student_id, {})
        rec = recs_map.get(student_id, {})
        
        missing_skills = profile.get('skill_gaps', {}).get('missing_skills', [])
        
        # Initialize Roadmap
        roadmap = {
            "student_id": student_id,
            "career_path": career,
            "career_source": source,
            "generated_at": "2025-11-29",
            "certification_path": CERT_PATHS.get(career, []),
            "stages": []
        }
        
        # Define Stages
        stages_config = [
            ("Beginner", "4-6 weeks", "Fundamentals & Top Gaps", missing_skills[:5]),
            ("Intermediate", "6-8 weeks", "Application & Certification", missing_skills[5:10] if len(missing_skills) > 5 else []),
            ("Advanced", "8-10 weeks", "Mastery & Job Readiness", missing_skills[10:15] if len(missing_skills) > 10 else [])
        ]
        
        rec_courses = rec.get('recommended_courses', [])
        n_courses = len(rec_courses)
        c_idx = 0
        
        for name, duration, focus, skills in stages_config:
            stage_data = {
                "stage": name,
                "duration": duration,
                "focus": focus,
                "skills": skills,
                "courses": [],
                "projects": []
            }
            
            # Distribute courses (approx 1/3 per stage)
            count = max(1, int(n_courses / 3))
            # Ensure we don't go out of bounds
            end_idx = min(c_idx + count, n_courses)
            stage_data["courses"] = rec_courses[c_idx : end_idx]
            c_idx = end_idx
            
            # Add Project Template
            proj = get_project_template(career, name)
            stage_data["projects"].append(proj)
            
            # Add Recommended Projects if they match difficulty (Optional enhancement)
            rec_projects = rec.get('recommended_projects', [])
            for p in rec_projects:
                if p.get('difficulty') == name:
                    stage_data["projects"].append(p)
            
            # Add Internships to Advanced Stage
            if name == "Advanced":
                stage_data["internships"] = rec.get('recommended_internships', [])[:3]
            
            roadmap["stages"].append(stage_data)
            
        # Save
        with open(ROADMAPS_DIR / f"{student_id}_roadmap.json", "w") as f:
            json.dump(roadmap, f, indent=2)
            
        generated_count += 1
        
    print(f"\n✅ Generated {generated_count} roadmaps in 'roadmaps/' directory.")
    print("=" * 70)

if __name__ == "__main__":
    main()
