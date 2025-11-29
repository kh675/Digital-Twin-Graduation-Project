"""
Skill Gap Analysis Engine - Step 2
Compares students to jobs, identifies skill gaps, and generates comprehensive profiles.
"""

import os
import sys
import pickle
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


def cosine_similarity_numpy(X, Y):
    """
    Compute cosine similarity between two matrices using numpy.
    Avoids scikit-learn DLL issues on Windows.
    
    Args:
        X: Matrix of shape (n_samples_X, n_features)
        Y: Matrix of shape (n_samples_Y, n_features)
    
    Returns:
        Similarity matrix of shape (n_samples_X, n_samples_Y)
    """
    # Normalize rows
    X_norm = X / np.linalg.norm(X, axis=1, keepdims=True)
    Y_norm = Y / np.linalg.norm(Y, axis=1, keepdims=True)
    
    # Compute dot product
    return np.dot(X_norm, Y_norm.T)


# Configure UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import skill parsing utilities
from utils.skill_parser import (
    parse_skill_list,
    merge_skill_sets,
    calculate_skill_overlap,
    extract_skill_frequency,
    get_top_skills
)


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_progress(text):
    """Print progress message"""
    print(f"[*] {text}")


def load_embeddings():
    """Load all embeddings from Step 1"""
    print_header("LOADING EMBEDDINGS")
    
    embeddings_dir = 'embeddings'
    embeddings = {}
    
    files = {
        'students': 'embeddings_students.pkl',
        'jobs': 'embeddings_jobs.pkl',
        'courses': 'embeddings_courses.pkl',
        'interests': 'embeddings_interests.pkl'
    }
    
    for key, filename in files.items():
        filepath = os.path.join(embeddings_dir, filename)
        print_progress(f"Loading {filename}...")
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            embeddings[key] = data
            print(f"    - Loaded {len(data['ids'])} {key} embeddings")
            print(f"    - Shape: {data['embeddings'].shape}")
    
    print("\n[SUCCESS] All embeddings loaded successfully!")
    return embeddings


def load_datasets():
    """Load original datasets for skill extraction"""
    print_header("LOADING DATASETS")
    
    datasets = {}
    
    files = {
        'students': 'students_1500_PRODUCTION_READY.csv',
        'jobs': 'egypt_jobs_full_1500_cleaned.csv',
        'courses': 'digital_twin_courses_1500_cleaned.csv'
    }
    
    for key, filename in files.items():
        print_progress(f"Loading {filename}...")
        df = pd.read_csv(filename, encoding='utf-8')
        datasets[key] = df
        print(f"    - Loaded {len(df)} rows, {len(df.columns)} columns")
    
    print("\n[SUCCESS] All datasets loaded successfully!")
    return datasets


def compute_similarity_matrix(student_embeddings, job_embeddings):
    """Compute cosine similarity between students and jobs"""
    print_header("COMPUTING SIMILARITY MATRIX")
    
    print_progress("Calculating cosine similarity (1500 x 1500)...")
    similarity_matrix = cosine_similarity_numpy(student_embeddings, job_embeddings)
    
    print(f"    - Matrix shape: {similarity_matrix.shape}")
    print(f"    - Min similarity: {similarity_matrix.min():.4f}")
    print(f"    - Max similarity: {similarity_matrix.max():.4f}")
    print(f"    - Mean similarity: {similarity_matrix.mean():.4f}")
    
    print("\n[SUCCESS] Similarity matrix computed!")
    return similarity_matrix


def get_top_job_matches(similarity_matrix, job_ids, job_df, top_n=5):
    """Get top N job matches for each student"""
    print_header(f"EXTRACTING TOP {top_n} JOB MATCHES PER STUDENT")
    
    num_students = similarity_matrix.shape[0]
    all_matches = []
    
    for student_idx in range(num_students):
        # Get similarity scores for this student
        scores = similarity_matrix[student_idx]
        
        # Get top N job indices
        top_indices = np.argsort(scores)[-top_n:][::-1]
        
        # Extract job details
        matches = []
        for job_idx in top_indices:
            job_id = job_ids[job_idx]
            job_row = job_df[job_df['job_id'] == job_id].iloc[0]
            
            matches.append({
                'job_id': job_id,
                'job_title': job_row['job_title'],
                'company': job_row['company'],
                'location': job_row['location'],
                'department': job_row['department'],
                'job_level': job_row['job_level'],
                'similarity_score': float(scores[job_idx]),
                'match_percentage': float(scores[job_idx] * 100)
            })
        
        all_matches.append(matches)
        
        if (student_idx + 1) % 300 == 0:
            print_progress(f"Processed {student_idx + 1}/{num_students} students...")
    
    print(f"\n[SUCCESS] Extracted top {top_n} matches for all {num_students} students!")
    return all_matches


def extract_student_skills(student_row):
    """Extract and merge all skills for a student"""
    skill_columns = ['Skills', 'TechnicalSkills', 'SoftSkills']
    skill_lists = []
    
    for col in skill_columns:
        if col in student_row.index and pd.notna(student_row[col]):
            skills = parse_skill_list(str(student_row[col]))
            skill_lists.append(skills)
    
    return merge_skill_sets(*skill_lists)


def extract_job_skills(job_row):
    """Extract skills required for a job"""
    if 'required_skills' in job_row.index and pd.notna(job_row['required_skills']):
        return parse_skill_list(str(job_row['required_skills']))
    return []


def analyze_skill_gaps(student_skills, job_matches, job_df):
    """Analyze skill gaps between student and their top job matches"""
    all_missing_skills = []
    all_matching_skills = []
    job_skill_lists = []
    
    for match in job_matches:
        job_id = match['job_id']
        job_row = job_df[job_df['job_id'] == job_id].iloc[0]
        job_skills = extract_job_skills(job_row)
        job_skill_lists.append(job_skills)
        
        # Calculate overlap
        overlap = calculate_skill_overlap(student_skills, job_skills)
        all_missing_skills.extend(overlap['missing_from_1'])
        all_matching_skills.extend(overlap['matching'])
    
    # Get unique skills
    unique_missing = list(set(all_missing_skills))
    unique_matching = list(set(all_matching_skills))
    
    # Calculate skill priorities
    skill_frequency = extract_skill_frequency(job_skill_lists)
    
    # Prioritize missing skills by frequency
    priority_skills = []
    for skill in unique_missing:
        frequency = skill_frequency.get(skill, 0)
        priority_score = frequency / len(job_matches) * 10  # Scale to 0-10
        
        priority_skills.append({
            'skill': skill,
            'priority_score': round(priority_score, 2),
            'appears_in_jobs': frequency
        })
    
    # Sort by priority score
    priority_skills.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return {
        'missing_skills': sorted(unique_missing),
        'matching_skills': sorted(unique_matching),
        'priority_skills': priority_skills
    }


def generate_recommendations(skill_gaps, job_matches):
    """Generate skill recommendations based on gaps and job matches"""
    priority_skills = skill_gaps['priority_skills']
    
    # Immediate focus: top 3 priority skills
    immediate_focus = [s['skill'] for s in priority_skills[:3]]
    
    # Secondary skills: next 3-5 priority skills
    secondary_skills = [s['skill'] for s in priority_skills[3:8]]
    
    # Career paths: unique job titles from top matches
    career_paths = list(set([match['job_title'] for match in job_matches[:3]]))
    
    return {
        'immediate_focus': immediate_focus,
        'secondary_skills': secondary_skills,
        'career_paths': career_paths
    }


def generate_skill_gap_profiles(embeddings, datasets, similarity_matrix, top_job_matches):
    """Generate comprehensive skill gap profiles for all students"""
    print_header("GENERATING SKILL GAP PROFILES")
    
    student_df = datasets['students']
    job_df = datasets['jobs']
    
    profiles = []
    
    for idx, student_id in enumerate(embeddings['students']['ids']):
        student_row = student_df[student_df['StudentID'] == student_id].iloc[0]
        
        # Extract student skills
        student_skills = extract_student_skills(student_row)
        
        # Get job matches
        job_matches = top_job_matches[idx]
        
        # Analyze skill gaps
        skill_gaps = analyze_skill_gaps(student_skills, job_matches, job_df)
        
        # Generate recommendations
        recommendations = generate_recommendations(skill_gaps, job_matches)
        
        # Build profile
        profile = {
            'student_id': student_id,
            'student_name': student_row['FullName'],
            'department': student_row['Department'],
            'gpa': float(student_row['GPA']),
            'academic_year': int(student_row['AcademicYear']),
            'current_skills': student_skills,
            'skill_count': len(student_skills),
            'best_job_matches': job_matches,
            'skill_gaps': skill_gaps,
            'recommendations': recommendations,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        profiles.append(profile)
        
        if (idx + 1) % 300 == 0:
            print_progress(f"Generated profiles for {idx + 1}/{len(embeddings['students']['ids'])} students...")
    
    print(f"\n[SUCCESS] Generated {len(profiles)} complete skill gap profiles!")
    return profiles


def save_profiles(profiles):
    """Save profiles to JSON files"""
    print_header("SAVING PROFILES")
    
    # Create output directory
    output_dir = 'skill_gap_profiles'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save all profiles
    print_progress("Saving student_profiles.json...")
    with open(os.path.join(output_dir, 'student_profiles.json'), 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    
    # Generate summary statistics
    print_progress("Generating summary statistics...")
    summary = {
        'total_students': len(profiles),
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'average_skills_per_student': round(np.mean([p['skill_count'] for p in profiles]), 2),
        'average_missing_skills': round(np.mean([len(p['skill_gaps']['missing_skills']) for p in profiles]), 2),
        'average_matching_skills': round(np.mean([len(p['skill_gaps']['matching_skills']) for p in profiles]), 2),
        'top_departments': {},
        'average_match_score_by_department': {}
    }
    
    # Department statistics
    dept_counts = {}
    dept_match_scores = {}
    
    for profile in profiles:
        dept = profile['department']
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        avg_match = np.mean([m['match_percentage'] for m in profile['best_job_matches']])
        if dept not in dept_match_scores:
            dept_match_scores[dept] = []
        dept_match_scores[dept].append(avg_match)
    
    summary['top_departments'] = dept_counts
    summary['average_match_score_by_department'] = {
        dept: round(np.mean(scores), 2)
        for dept, scores in dept_match_scores.items()
    }
    
    # Save summary
    with open(os.path.join(output_dir, 'summary_statistics.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Extract top missing skills across all students
    print_progress("Extracting top missing skills...")
    all_missing_skills = []
    for profile in profiles:
        all_missing_skills.extend(profile['skill_gaps']['missing_skills'])
    
    skill_frequency = {}
    for skill in all_missing_skills:
        skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
    
    top_missing = get_top_skills(skill_frequency, top_n=50)
    
    # Save as CSV
    top_missing_df = pd.DataFrame(top_missing, columns=['Skill', 'Frequency'])
    top_missing_df.to_csv(os.path.join(output_dir, 'top_missing_skills.csv'), index=False)
    
    print(f"\n[SUCCESS] All files saved to '{output_dir}/' directory!")
    print(f"    - student_profiles.json ({len(profiles)} profiles)")
    print(f"    - summary_statistics.json")
    print(f"    - top_missing_skills.csv (top 50 skills)")


def main():
    """Main execution function"""
    print_header("SKILL GAP ANALYSIS ENGINE - STEP 2")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Load embeddings
        embeddings = load_embeddings()
        
        # Load datasets
        datasets = load_datasets()
        
        # Compute similarity matrix
        similarity_matrix = compute_similarity_matrix(
            embeddings['students']['embeddings'],
            embeddings['jobs']['embeddings']
        )
        
        # Get top job matches
        top_job_matches = get_top_job_matches(
            similarity_matrix,
            embeddings['jobs']['ids'],
            datasets['jobs'],
            top_n=5
        )
        
        # Generate skill gap profiles
        profiles = generate_skill_gap_profiles(
            embeddings,
            datasets,
            similarity_matrix,
            top_job_matches
        )
        
        # Save profiles
        save_profiles(profiles)
        
        print_header("ANALYSIS COMPLETE!")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nNext Steps:")
        print("  1. Run 'python verify_skill_gaps.py' to validate results")
        print("  2. Review profiles in 'skill_gap_profiles/' directory")
        print("  3. Proceed to Step 3: Recommendation Engine\n")
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
