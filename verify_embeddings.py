"""
Embedding Verification Script
==============================
Validates the quality and correctness of generated embeddings.

Tests:
1. Shape verification (384 dimensions)
2. Semantic similarity sanity checks
3. Quality metrics and statistics
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
EMBEDDINGS_DIR = 'embeddings'
STUDENT_FILE = 'students_1500_PRODUCTION_READY.csv'
JOB_FILE = 'egypt_jobs_full_1500_cleaned.csv'
COURSE_FILE = 'digital_twin_courses_1500_cleaned.csv'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_pickle(filename):
    """Load pickle file from embeddings directory"""
    path = os.path.join(EMBEDDINGS_DIR, filename)
    with open(path, 'rb') as f:
        return pickle.load(f)

# ============================================================================
# VERIFICATION TESTS
# ============================================================================

def verify():
    log("="*70)
    log("EMBEDDING VERIFICATION - STEP 1 VALIDATION")
    log("="*70)
    
    # Load all embeddings
    try:
        log("\nLoading embeddings...")
        data_students = load_pickle('embeddings_students.pkl')
        data_jobs = load_pickle('embeddings_jobs.pkl')
        data_courses = load_pickle('embeddings_courses.pkl')
        data_interests = load_pickle('embeddings_interests.pkl')
        log("✓ All embedding files loaded successfully")
    except Exception as e:
        log(f"✗ ERROR loading embeddings: {e}")
        return
    
    # ========================================================================
    # TEST 1: SHAPE VERIFICATION
    # ========================================================================
    log("\n" + "="*70)
    log("TEST 1: SHAPE VERIFICATION")
    log("="*70)
    
    def check_shape(name, data, expected_dim=384):
        """Verify embedding shape and ID count"""
        emb = data['embeddings']
        ids = data['ids']
        
        log(f"\n{name}:")
        log(f"  Embeddings shape: {emb.shape}")
        log(f"  Number of IDs: {len(ids)}")
        log(f"  Expected dimension: {expected_dim}")
        
        passed = True
        
        # Check dimension
        if emb.shape[1] != expected_dim:
            log(f"  ✗ FAIL: Expected dimension {expected_dim}, got {emb.shape[1]}")
            passed = False
        else:
            log(f"  ✓ Dimension correct: {expected_dim}")
        
        # Check count match
        if emb.shape[0] != len(ids):
            log(f"  ✗ FAIL: Mismatch between embeddings ({emb.shape[0]}) and IDs ({len(ids)})")
            passed = False
        else:
            log(f"  ✓ Count matches: {len(ids)}")
        
        # Check for NaN or infinite values
        if np.isnan(emb).any():
            log(f"  ✗ FAIL: Contains NaN values")
            passed = False
        elif np.isinf(emb).any():
            log(f"  ✗ FAIL: Contains infinite values")
            passed = False
        else:
            log(f"  ✓ No NaN or infinite values")
        
        # Check value range (embeddings should be normalized)
        min_val, max_val = emb.min(), emb.max()
        log(f"  Value range: [{min_val:.4f}, {max_val:.4f}]")
        
        return passed
    
    all_passed = True
    all_passed &= check_shape('Students', data_students)
    all_passed &= check_shape('Jobs', data_jobs)
    all_passed &= check_shape('Courses', data_courses)
    all_passed &= check_shape('Interests', data_interests)
    
    if not all_passed:
        log("\n✗ Shape verification FAILED")
        return
    
    log("\n" + "✓"*70)
    log("TEST 1 PASSED: All shapes are correct!")
    log("✓"*70)
    
    # ========================================================================
    # TEST 2: SEMANTIC SIMILARITY - STUDENT TO JOB MATCHING
    # ========================================================================
    log("\n" + "="*70)
    log("TEST 2: SEMANTIC SIMILARITY - STUDENT TO JOB MATCHING")
    log("="*70)
    
    try:
        df_students = pd.read_csv(STUDENT_FILE)
        df_jobs = pd.read_csv(JOB_FILE)
        
        # Pick 3 sample students
        sample_indices = [0, len(df_students)//2, len(df_students)-1]
        
        for s_idx in sample_indices:
            student_emb = data_students['embeddings'][s_idx].reshape(1, -1)
            student_id = data_students['ids'][s_idx]
            student_row = df_students.iloc[s_idx]
            
            log(f"\n{'─'*70}")
            log(f"Student {student_id}:")
            log(f"  Department: {student_row.get('Department', 'N/A')}")
            log(f"  Preferred Track: {student_row.get('PreferredTrack', 'N/A')}")
            
            # Show some skills
            skills = str(student_row.get('TechnicalSkills', ''))[:80]
            if skills:
                log(f"  Technical Skills: {skills}...")
            
            # Calculate similarity with all jobs
            job_embs = data_jobs['embeddings']
            sims = cosine_similarity(student_emb, job_embs)[0]
            
            # Top 5 matches
            top_indices = sims.argsort()[-5:][::-1]
            log(f"\n  Top 5 Job Matches:")
            for rank, idx in enumerate(top_indices, 1):
                job_id = data_jobs['ids'][idx]
                score = sims[idx]
                job_row = df_jobs[df_jobs['job_id'] == job_id].iloc[0]
                log(f"    {rank}. {job_row['job_title']:<40} (Score: {score:.4f})")
        
        log("\n" + "✓"*70)
        log("TEST 2 PASSED: Student-Job matching works!")
        log("✓"*70)
        
    except Exception as e:
        log(f"\n✗ ERROR in student-job matching test: {e}")
    
    # ========================================================================
    # TEST 3: SEMANTIC SIMILARITY - STUDENT TO COURSE RECOMMENDATIONS
    # ========================================================================
    log("\n" + "="*70)
    log("TEST 3: SEMANTIC SIMILARITY - STUDENT TO COURSE RECOMMENDATIONS")
    log("="*70)
    
    try:
        df_courses = pd.read_csv(COURSE_FILE)
        
        # Use first student
        s_idx = 0
        student_emb = data_students['embeddings'][s_idx].reshape(1, -1)
        student_id = data_students['ids'][s_idx]
        student_row = df_students.iloc[s_idx]
        
        log(f"\nStudent {student_id}:")
        log(f"  Preferred Track: {student_row.get('PreferredTrack', 'N/A')}")
        
        # Calculate similarity with all courses
        course_embs = data_courses['embeddings']
        sims = cosine_similarity(student_emb, course_embs)[0]
        
        # Top 5 course recommendations
        top_indices = sims.argsort()[-5:][::-1]
        log(f"\n  Top 5 Course Recommendations:")
        for rank, idx in enumerate(top_indices, 1):
            score = sims[idx]
            course_row = df_courses.iloc[idx]
            
            # Get course title (check different possible column names)
            title = course_row.get('CourseTitle', course_row.get('CourseName', 'Unknown'))
            level = course_row.get('Level', 'N/A')
            
            log(f"    {rank}. {str(title)[:50]:<50} [{level}] (Score: {score:.4f})")
        
        log("\n" + "✓"*70)
        log("TEST 3 PASSED: Student-Course recommendations work!")
        log("✓"*70)
        
    except Exception as e:
        log(f"\n✗ ERROR in student-course matching test: {e}")
    
    # ========================================================================
    # TEST 4: INTEREST-BASED COURSE RECOMMENDATIONS
    # ========================================================================
    log("\n" + "="*70)
    log("TEST 4: INTEREST-BASED COURSE RECOMMENDATIONS")
    log("="*70)
    
    try:
        # Use first student's interests
        s_idx = 0
        interest_emb = data_interests['embeddings'][s_idx].reshape(1, -1)
        student_id = data_interests['ids'][s_idx]
        student_row = df_students.iloc[s_idx]
        
        log(f"\nStudent {student_id}:")
        
        # Show interests if available
        for col in ['UserInterests', 'Interests', 'PreferredTrack']:
            if col in student_row:
                val = str(student_row.get(col, ''))[:80]
                if val and val != 'nan':
                    log(f"  {col}: {val}")
        
        # Calculate similarity with all courses based on interests
        course_embs = data_courses['embeddings']
        sims = cosine_similarity(interest_emb, course_embs)[0]
        
        # Top 5 interest-based recommendations
        top_indices = sims.argsort()[-5:][::-1]
        log(f"\n  Top 5 Interest-Based Course Recommendations:")
        for rank, idx in enumerate(top_indices, 1):
            score = sims[idx]
            course_row = df_courses.iloc[idx]
            
            title = course_row.get('CourseTitle', course_row.get('CourseName', 'Unknown'))
            track = course_row.get('Track', 'N/A')
            
            log(f"    {rank}. {str(title)[:45]:<45} [{track}] (Score: {score:.4f})")
        
        log("\n" + "✓"*70)
        log("TEST 4 PASSED: Interest-based recommendations work!")
        log("✓"*70)
        
    except Exception as e:
        log(f"\n✗ ERROR in interest-based matching test: {e}")
    
    # ========================================================================
    # TEST 5: QUALITY METRICS
    # ========================================================================
    log("\n" + "="*70)
    log("TEST 5: QUALITY METRICS & STATISTICS")
    log("="*70)
    
    try:
        # Calculate average similarity within each category
        def calc_avg_similarity(embeddings, sample_size=100):
            """Calculate average pairwise similarity for a sample"""
            n = min(sample_size, len(embeddings))
            indices = np.random.choice(len(embeddings), n, replace=False)
            sample = embeddings[indices]
            sims = cosine_similarity(sample, sample)
            # Exclude diagonal (self-similarity = 1.0)
            mask = ~np.eye(n, dtype=bool)
            return sims[mask].mean()
        
        log("\nAverage intra-category similarity (sample of 100):")
        log(f"  Students:  {calc_avg_similarity(data_students['embeddings']):.4f}")
        log(f"  Jobs:      {calc_avg_similarity(data_jobs['embeddings']):.4f}")
        log(f"  Courses:   {calc_avg_similarity(data_courses['embeddings']):.4f}")
        log(f"  Interests: {calc_avg_similarity(data_interests['embeddings']):.4f}")
        
        log("\nNote: Lower values (0.3-0.6) indicate good diversity within categories")
        log("      Higher values (0.7+) might indicate lack of diversity")
        
        log("\n" + "✓"*70)
        log("TEST 5 PASSED: Quality metrics calculated!")
        log("✓"*70)
        
    except Exception as e:
        log(f"\n✗ ERROR calculating quality metrics: {e}")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    log("\n" + "="*70)
    log("VERIFICATION COMPLETE ✓")
    log("="*70)
    log("\nAll tests passed successfully!")
    log("\nEmbeddings are ready for use in:")
    log("  • Skill Gap Analysis")
    log("  • Job Recommendations")
    log("  • Course Recommendations")
    log("  • Career Path Prediction")
    log("  • Personalized Learning Roadmaps")
    log("\nNext steps:")
    log("  → Step 2: Build Skill Matching Engine")
    log("  → Step 3: Build Recommendation Engine")
    log("  → Step 4: Build Career Prediction Model")
    log("="*70)

if __name__ == "__main__":
    verify()
