"""
Skill Embeddings Generator
===========================
Transforms student skills, job requirements, course content, and interests
into 384-dimensional numerical vectors using Sentence Transformers.

Model: all-MiniLM-L6-v2 (lightweight, fast, perfect for similarity matching)
Used by: LinkedIn, Coursera, Udemy recommendation systems
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
MODEL_NAME = 'all-MiniLM-L6-v2'
STUDENT_FILE = 'students_1500_PRODUCTION_READY.csv'
JOB_FILE = 'egypt_jobs_full_1500_cleaned.csv'
COURSE_FILE = 'digital_twin_courses_1500_cleaned.csv'

OUTPUT_DIR = 'embeddings'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def safe_str(value):
    """Safely convert value to string, handling NaN"""
    if pd.isna(value):
        return ""
    return str(value).strip()

def combine_fields(row, fields):
    """Combine multiple fields into a single text string"""
    parts = []
    for field in fields:
        value = safe_str(row.get(field, ""))
        if value:
            parts.append(value)
    return " ".join(parts)

def filter_high_grades(grades_str):
    """Extract subjects with high grades (A or B) from grade string"""
    if pd.isna(grades_str) or not grades_str:
        return ""
    
    # Format: "Math: A; Physics: B; Chemistry: C"
    high_grade_subjects = []
    try:
        for item in str(grades_str).split(';'):
            item = item.strip()
            if ':' in item:
                subject, grade = item.split(':', 1)
                grade = grade.strip().upper()
                if grade in ['A', 'A+', 'A-', 'B', 'B+']:
                    high_grade_subjects.append(subject.strip())
    except:
        pass
    
    return " ".join(high_grade_subjects)

# ============================================================================
# MAIN EMBEDDING GENERATION
# ============================================================================

def generate_embeddings():
    log("="*70)
    log("SKILL EMBEDDINGS GENERATION - STEP 1")
    log("="*70)
    
    # Load model
    log(f"Loading Sentence Transformer model: {MODEL_NAME}")
    log("This may take a few minutes on first run (downloading model)...")
    try:
        model = SentenceTransformer(MODEL_NAME, device='cpu')
        log(f"[OK] Model loaded successfully (embedding dimension: 384)")
    except Exception as e:
        log(f"[ERROR] Failed to load model: {e}")
        log("")
        log("TROUBLESHOOTING:")
        log("  1. Close other applications to free up memory")
        log("  2. Restart your computer to clear memory")
        log("  3. Try running this script again")
        return
    
    # Metadata to save with embeddings
    metadata = {
        'model_name': MODEL_NAME,
        'embedding_dim': 384,
        'generated_at': datetime.now().isoformat(),
        'datasets': {
            'students': STUDENT_FILE,
            'jobs': JOB_FILE,
            'courses': COURSE_FILE
        }
    }
    
    # ========================================================================
    # 1. STUDENT SKILL EMBEDDINGS
    # ========================================================================
    log("\n" + "="*70)
    log("1. GENERATING STUDENT SKILL EMBEDDINGS")
    log("="*70)
    
    try:
        df_students = pd.read_csv(STUDENT_FILE)
        log(f"[OK] Loaded {len(df_students)} students from {STUDENT_FILE}")
        
        # Combine fields for Student Skill Vector
        # Fields: Skills, TechnicalSkills, SoftSkills, CoursesCompleted, 
        #         MajorCourseGrades (high grades), Projects
        def combine_student_skills(row):
            parts = []
            
            # Core skills
            parts.append(safe_str(row.get('Skills')))
            parts.append(safe_str(row.get('TechnicalSkills')))
            parts.append(safe_str(row.get('SoftSkills')))
            
            # Completed courses show acquired skills
            parts.append(safe_str(row.get('CoursesCompleted')))
            
            # High-grade subjects indicate strengths
            if 'MajorCourseGrades' in row:
                high_grade_subjects = filter_high_grades(row['MajorCourseGrades'])
                parts.append(high_grade_subjects)
            
            # Projects show applied skills
            parts.append(safe_str(row.get('Projects')))
            
            return " ".join([p for p in parts if p])
        
        student_texts = df_students.apply(combine_student_skills, axis=1).tolist()
        student_ids = df_students['StudentID'].tolist()
        
        log(f"Processing {len(student_texts)} student skill vectors...")
        student_embeddings = model.encode(
            student_texts, 
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        
        # Save
        output_path = os.path.join(OUTPUT_DIR, 'embeddings_students.pkl')
        with open(output_path, 'wb') as f:
            pickle.dump({
                'ids': student_ids,
                'embeddings': student_embeddings,
                'metadata': metadata
            }, f)
        
        log(f"[OK] Saved {len(student_embeddings)} student embeddings to {output_path}")
        log(f"  Shape: {student_embeddings.shape}")
        
    except Exception as e:
        log(f"[ERROR] Failed to generate student embeddings: {e}")
        return
    
    # ========================================================================
    # 2. JOB SKILL EMBEDDINGS
    # ========================================================================
    log("\n" + "="*70)
    log("2. GENERATING JOB SKILL EMBEDDINGS")
    log("="*70)
    
    try:
        df_jobs = pd.read_csv(JOB_FILE)
        log(f"[OK] Loaded {len(df_jobs)} jobs from {JOB_FILE}")
        
        # Combine: job_title, required_skills, certificates, responsibilities
        def combine_job_skills(row):
            parts = []
            
            parts.append(safe_str(row.get('job_title')))
            parts.append(safe_str(row.get('required_skills')))
            
            # Check for various possible column names
            for cert_col in ['certificates', 'certificates_required', 'required_certificates']:
                if cert_col in row:
                    parts.append(safe_str(row.get(cert_col)))
                    break
            
            for resp_col in ['responsibilities', 'job_description', 'description']:
                if resp_col in row:
                    parts.append(safe_str(row.get(resp_col)))
                    break
            
            return " ".join([p for p in parts if p])
        
        job_texts = df_jobs.apply(combine_job_skills, axis=1).tolist()
        job_ids = df_jobs['job_id'].tolist() if 'job_id' in df_jobs.columns else list(range(len(df_jobs)))
        
        log(f"Processing {len(job_texts)} job skill vectors...")
        job_embeddings = model.encode(
            job_texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        
        # Save
        output_path = os.path.join(OUTPUT_DIR, 'embeddings_jobs.pkl')
        with open(output_path, 'wb') as f:
            pickle.dump({
                'ids': job_ids,
                'embeddings': job_embeddings,
                'metadata': metadata
            }, f)
        
        log(f"[OK] Saved {len(job_embeddings)} job embeddings to {output_path}")
        log(f"  Shape: {job_embeddings.shape}")
        
    except Exception as e:
        log(f"[ERROR] Failed to generate job embeddings: {e}")
        return
    
    # ========================================================================
    # 3. COURSE SKILL EMBEDDINGS
    # ========================================================================
    log("\n" + "="*70)
    log("3. GENERATING COURSE SKILL EMBEDDINGS")
    log("="*70)
    
    try:
        df_courses = pd.read_csv(COURSE_FILE)
        log(f"[OK] Loaded {len(df_courses)} courses from {COURSE_FILE}")
        
        # Combine: CourseTitle, Description, SkillsGained, Level, Track
        def combine_course_skills(row):
            parts = []
            
            # Check for various possible column names
            for title_col in ['CourseTitle', 'CourseName', 'Title', 'title']:
                if title_col in row:
                    parts.append(safe_str(row.get(title_col)))
                    break
            
            parts.append(safe_str(row.get('Description')))
            parts.append(safe_str(row.get('SkillsGained')))
            parts.append(safe_str(row.get('Level')))
            parts.append(safe_str(row.get('Track')))
            
            return " ".join([p for p in parts if p])
        
        course_texts = df_courses.apply(combine_course_skills, axis=1).tolist()
        
        # Try to get CourseID, fall back to index
        if 'CourseID' in df_courses.columns:
            course_ids = df_courses['CourseID'].tolist()
        elif 'course_id' in df_courses.columns:
            course_ids = df_courses['course_id'].tolist()
        else:
            course_ids = list(range(len(df_courses)))
        
        log(f"Processing {len(course_texts)} course skill vectors...")
        course_embeddings = model.encode(
            course_texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        
        # Save
        output_path = os.path.join(OUTPUT_DIR, 'embeddings_courses.pkl')
        with open(output_path, 'wb') as f:
            pickle.dump({
                'ids': course_ids,
                'embeddings': course_embeddings,
                'metadata': metadata
            }, f)
        
        log(f"[OK] Saved {len(course_embeddings)} course embeddings to {output_path}")
        log(f"  Shape: {course_embeddings.shape}")
        
    except Exception as e:
        log(f"[ERROR] Failed to generate course embeddings: {e}")
        return
    
    # ========================================================================
    # 4. STUDENT INTEREST EMBEDDINGS
    # ========================================================================
    log("\n" + "="*70)
    log("4. GENERATING STUDENT INTEREST EMBEDDINGS")
    log("="*70)
    
    try:
        # Combine: UserInterests, PreferredTrack, Extracurriculars, Projects
        def combine_student_interests(row):
            parts = []
            
            # Check for various possible column names
            for interest_col in ['UserInterests', 'Interests', 'interests']:
                if interest_col in row:
                    parts.append(safe_str(row.get(interest_col)))
                    break
            
            parts.append(safe_str(row.get('PreferredTrack')))
            parts.append(safe_str(row.get('Extracurriculars')))
            parts.append(safe_str(row.get('Projects')))
            
            return " ".join([p for p in parts if p])
        
        interest_texts = df_students.apply(combine_student_interests, axis=1).tolist()
        
        log(f"Processing {len(interest_texts)} interest vectors...")
        interest_embeddings = model.encode(
            interest_texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        
        # Save
        output_path = os.path.join(OUTPUT_DIR, 'embeddings_interests.pkl')
        with open(output_path, 'wb') as f:
            pickle.dump({
                'ids': student_ids,  # Same IDs as students
                'embeddings': interest_embeddings,
                'metadata': metadata
            }, f)
        
        log(f"[OK] Saved {len(interest_embeddings)} interest embeddings to {output_path}")
        log(f"  Shape: {interest_embeddings.shape}")
        
    except Exception as e:
        log(f"[ERROR] Failed to generate interest embeddings: {e}")
        return
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    log("\n" + "="*70)
    log("EMBEDDING GENERATION COMPLETE [SUCCESS]")
    log("="*70)
    log(f"All embeddings saved to: {OUTPUT_DIR}/")
    log(f"")
    log(f"Files created:")
    log(f"  - embeddings_students.pkl   ({len(student_embeddings)} vectors)")
    log(f"  - embeddings_jobs.pkl       ({len(job_embeddings)} vectors)")
    log(f"  - embeddings_courses.pkl    ({len(course_embeddings)} vectors)")
    log(f"  - embeddings_interests.pkl  ({len(interest_embeddings)} vectors)")
    log(f"")
    log(f"Next step: Run verify_embeddings.py to validate the embeddings")
    log("="*70)

if __name__ == "__main__":
    generate_embeddings()
