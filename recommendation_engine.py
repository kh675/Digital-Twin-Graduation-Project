import pandas as pd
import numpy as np
import pickle
import json
import os
import random
from datetime import datetime
from utils.skill_parser import parse_skill_list, normalize_skill

# --- Configuration ---
INPUT_DIR = "skill_gap_profiles"
EMBEDDING_DIR = "embeddings"
OUTPUT_DIR = "recommendations"
COURSE_DATA_PATH = "digital_twin_courses_1500_cleaned.csv"
JOB_DATA_PATH = "egypt_jobs_full_1500_cleaned.csv"

# --- Helper Functions ---

def cosine_similarity_numpy(v1, v2):
    """Compute cosine similarity between two vectors or matrices."""
    try:
        # Ensure inputs are numpy arrays
        v1 = np.array(v1, dtype=np.float32)
        v2 = np.array(v2, dtype=np.float32)
        
        # Ensure inputs are 2D arrays
        if v1.ndim == 1:
            v1 = v1.reshape(1, -1)
        if v2.ndim == 1:
            v2 = v2.reshape(1, -1)
            
        norm_v1 = np.linalg.norm(v1, axis=1, keepdims=True)
        norm_v2 = np.linalg.norm(v2, axis=1, keepdims=True)
        
        # Avoid division by zero
        norm_v1[norm_v1 == 0] = 1e-10
        norm_v2[norm_v2 == 0] = 1e-10
        
        return np.dot(v1, v2.T) / np.dot(norm_v1, norm_v2.T)
    except Exception as e:
        print(f"Error in cosine_similarity_numpy: {e}")
        print(f"v1 shape: {v1.shape if hasattr(v1, 'shape') else 'unknown'}, type: {type(v1)}")
        print(f"v2 shape: {v2.shape if hasattr(v2, 'shape') else 'unknown'}, type: {type(v2)}")
        raise e

def calculate_skill_coverage(missing_skills, course_skills):
    """Calculate the percentage of missing skills covered by the course."""
    if not missing_skills:
        return 0.0
    
    missing_set = set(missing_skills)
    course_set = set(course_skills)
    
    covered_count = len(missing_set.intersection(course_set))
    return covered_count / len(missing_set)

def get_level_score(level):
    """Return numerical score for course level."""
    level = str(level).lower().strip()
    if level == 'beginner':
        return 0.5
    elif level == 'intermediate':
        return 0.8
    elif level == 'advanced':
        return 1.0
    return 0.5 # Default

# --- Recommendation Engines ---

def recommend_courses(student_profile, student_embedding, course_embeddings, df_courses):
    """
    Generate course recommendations based on similarity, skill coverage, and level.
    """
    recommendations = []
    missing_skills = student_profile['skill_gaps']['missing_skills']
    completed_courses = set([c.lower().strip() for c in student_profile.get('current_courses', [])]) # Assuming 'current_courses' or similar field exists, or we parse from raw data if needed. 
    # Note: student_profile from Step 2 might not have raw course list, checking structure...
    # If not in profile, we might need to rely on the fact that we are recommending *new* things.
    # For now, let's assume we filter by exact name match if possible, or just recommend best fit.
    
    # Calculate Similarities (Student vs All Courses)
    # student_embedding is (1, 384), course_embeddings is (N, 384)
    similarities = cosine_similarity_numpy(student_embedding, course_embeddings).flatten()
    
    for idx, row in df_courses.iterrows():
        course_name = row['CourseTitle']
        
        # Skip if already completed (simple check)
        if course_name.lower().strip() in completed_courses:
            continue
            
        # 1. Similarity Score
        sim_score = similarities[idx]
        
        # 2. Skill Coverage Score
        course_skills = parse_skill_list(str(row['SkillsGained']))
        coverage_score = calculate_skill_coverage(missing_skills, course_skills)
        
        # 3. Level Score
        level_score = get_level_score(row['Level'])
        
        # Final Weighted Score
        # 0.60 * similarity + 0.30 * coverage + 0.10 * level
        final_score = (0.6 * sim_score) + (0.3 * coverage_score) + (0.1 * level_score)
        
        recommendations.append({
            "course_name": course_name,
            "provider": row['CourseProvider'],
            "level": row['Level'],
            "score": float(final_score),
            "similarity": float(sim_score),
            "coverage": float(coverage_score),
            "covers_skills": list(set(missing_skills).intersection(set(course_skills)))
        })
    
    # Sort by Score
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    # Get Top 5 AWS and Top 5 Huawei
    top_aws = [r for r in recommendations if r['provider'].upper() == 'AWS'][:5]
    top_huawei = [r for r in recommendations if r['provider'].upper() == 'HUAWEI'][:5]
    
    return top_aws + top_huawei

def recommend_skills(student_profile):
    """
    Return top 10 recommended skills based on priority score from Step 2.
    """
    priority_skills = student_profile['skill_gaps'].get('priority_skills', [])
    # Sort just in case, though Step 2 should have sorted them
    sorted_skills = sorted(priority_skills, key=lambda x: x['priority_score'], reverse=True)
    
    # Format for output
    recommended = []
    for item in sorted_skills[:10]:
        recommended.append({
            "skill": item['skill'],
            "priority": item['priority_score']
        })
    return recommended

def recommend_projects(student_profile, job_title):
    """
    Generate project ideas based on missing skills and target job.
    """
    missing_skills = student_profile['skill_gaps']['missing_skills']
    
    # If no missing skills, suggest advanced projects
    if not missing_skills:
        target_skills = ["Advanced Architecture", "Optimization"]
    else:
        # Pick top 2-3 missing skills
        target_skills = missing_skills[:3]
    
    skill_str = " & ".join([s.title() for s in target_skills])
    
    templates = [
        {
            "title": f"Build a {job_title} Pipeline using {skill_str}",
            "description": f"Create a comprehensive project that demonstrates your mastery of {skill_str}. Focus on real-world application.",
            "difficulty": "Intermediate"
        },
        {
            "title": f"Develop a Cloud-Native Application with {skill_str}",
            "description": f"Deploy a scalable application integrating {skill_str} to solve a specific business problem.",
            "difficulty": "Advanced"
        },
        {
            "title": f"{skill_str} Integration Lab",
            "description": f"Set up a practical lab environment to experiment with {skill_str} configurations and troubleshooting.",
            "difficulty": "Beginner"
        }
    ]
    
    # Add covered skills to output
    for t in templates:
        t['skills_covered'] = target_skills
        
    return templates

def recommend_internships(student_embedding, job_embeddings, df_jobs):
    """
    Recommend internships/junior roles based on similarity.
    """
    recommendations = []
    
    # Filter for Intern/Junior roles
    # We'll check the Job Title for keywords
    intern_indices = []
    for idx, row in df_jobs.iterrows():
        title = str(row['job_title']).lower()
        if 'intern' in title or 'junior' in title or 'trainee' in title or 'fresh' in title:
            intern_indices.append(idx)
            
    if not intern_indices:
        # Fallback: if no explicit intern roles, use all jobs but look for lower requirements?
        # For now, let's just use the top matches regardless if no interns found, 
        # but in a real scenario we might want to be stricter.
        # Let's try to find *any* match, if list is empty, return top general matches labeled as "Potential Entry Level"
        intern_indices = list(df_jobs.index)
    
    # Calculate similarity only for candidate jobs
    candidate_embeddings = job_embeddings[intern_indices]
    similarities = cosine_similarity_numpy(student_embedding, candidate_embeddings).flatten()
    
    # Create list of (original_idx, score)
    scored_candidates = []
    for i, original_idx in enumerate(intern_indices):
        scored_candidates.append((original_idx, similarities[i]))
        
    # Sort by similarity
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Top 5
    top_candidates = scored_candidates[:5]
    
    for original_idx, score in top_candidates:
        row = df_jobs.iloc[original_idx]
        recommendations.append({
            "company": row['company'],
            "role": row['job_title'],
            "match": float(score),
            "location": row.get('location', 'Egypt'), # Fallback
            "missing_skills": [] # Could populate this if we wanted to re-run gap analysis
        })
        
    return recommendations

# --- Main Execution ---

def main():
    print("🚀 Starting Step 3: Recommendation Engine...")
    
    # 1. Load Data
    print("   Loading data...")
    try:
        with open(os.path.join(INPUT_DIR, "student_profiles.json"), "r") as f:
            student_profiles = json.load(f)
            
        with open(os.path.join(EMBEDDING_DIR, "embeddings_students.pkl"), "rb") as f:
            student_data = pickle.load(f)
            student_embeddings = student_data['embeddings']
            # student_ids = student_data['ids'] # Not strictly needed if we assume 1:1 mapping with profiles
            
        with open(os.path.join(EMBEDDING_DIR, "embeddings_courses.pkl"), "rb") as f:
            course_data = pickle.load(f)
            course_embeddings = course_data['embeddings']
            course_ids = course_data['ids']
            
        with open(os.path.join(EMBEDDING_DIR, "embeddings_jobs.pkl"), "rb") as f:
            job_data = pickle.load(f)
            job_embeddings = job_data['embeddings']
            job_ids = job_data['ids']
            
        df_courses = pd.read_csv(COURSE_DATA_PATH)
        df_jobs = pd.read_csv(JOB_DATA_PATH)
        
        # Align DataFrames with Embeddings
        # We assume 'ids' in pickle correspond to DataFrame indices
        df_courses = df_courses.iloc[course_ids].reset_index(drop=True)
        
        # For jobs, ids are strings (J0001...), so we must set index first
        df_jobs = df_jobs.set_index('job_id').loc[job_ids].reset_index()
        
        print(f"   Loaded {len(student_profiles)} profiles.")
        print(f"   Aligned Data: {len(df_courses)} courses, {len(df_jobs)} jobs.")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    # 2. Generate Recommendations
    print("   Generating recommendations...")
    all_recommendations = []
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for i, profile in enumerate(student_profiles):
        student_id = profile.get('student_id', f"S{i:04d}")
        
        # Get student embedding (assuming aligned order, which they should be from Step 1 & 2)
        # Verify alignment if possible, but for now relying on index
        s_embedding = student_embeddings[i]
        
        # A. Course Recommendations
        rec_courses = recommend_courses(profile, s_embedding, course_embeddings, df_courses)
        
        # B. Skill Recommendations
        rec_skills = recommend_skills(profile)
        
        # C. Project Recommendations
        # Use the title of the #1 job match as the target
        top_job = profile['best_job_matches'][0]['job_title'] if profile['best_job_matches'] else "Cloud Engineer"
        rec_projects = recommend_projects(profile, top_job)
        
        # D. Internship Recommendations
        rec_internships = recommend_internships(s_embedding, job_embeddings, df_jobs)
        
        # Construct Final Object
        student_rec = {
            "student_id": student_id,
            "student_name": profile.get('student_name', 'Unknown'),
            "target_job": top_job,
            "recommended_courses": rec_courses,
            "recommended_skills": rec_skills,
            "recommended_projects": rec_projects,
            "recommended_internships": rec_internships,
            "comment": f"You are a {int(profile['best_job_matches'][0]['match_percentage'])}% match to {top_job} roles." if profile['best_job_matches'] else "Keep building your skills!"
        }
        
        all_recommendations.append(student_rec)
        
        if (i + 1) % 100 == 0:
            print(f"   Processed {i + 1}/{len(student_profiles)} students...")

    # 3. Save Output
    output_file = os.path.join(OUTPUT_DIR, "recommendations.json")
    with open(output_file, "w") as f:
        json.dump(all_recommendations, f, indent=2)
        
    print(f"✅ Successfully generated recommendations for {len(all_recommendations)} students.")
    print(f"📁 Output saved to: {output_file}")

if __name__ == "__main__":
    main()
