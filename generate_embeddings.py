import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from embedding_pipeline import SkillEmbeddingBuilder

def load_data():
    print("Loading data files...")
    
    # Base directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load the cleaned datasets with full paths
    courses_path = os.path.join(base_dir, 'digital_twin_courses_1500_cleaned.csv')
    students_path = os.path.join(base_dir, 'students_1500_PRODUCTION_READY.csv')
    jobs_path = os.path.join(base_dir, 'egypt_jobs_full_1500_cleaned.csv')
    
    print(f"Loading from:\n- {courses_path}\n- {students_path}\n- {jobs_path}")
    
    courses_df = pd.read_csv(courses_path)
    students_df = pd.read_csv(students_path)
    jobs_df = pd.read_csv(jobs_path)
    
    print(f"Loaded {len(students_df)} students, {len(jobs_df)} jobs, and {len(courses_df)} courses")
    return students_df, jobs_df, courses_df

def create_output_dir():
    """Create directory to save embeddings if it doesn't exist"""
    os.makedirs('embeddings', exist_ok=True)

def save_embeddings(embeddings, filename):
    """Save embeddings to numpy file"""
    np.save(f'embeddings/{filename}.npy', embeddings)
    print(f"Saved {filename} with shape {embeddings.shape}")

def main():
    # Create output directory
    create_output_dir()
    
    # Load data
    students_df, jobs_df, courses_df = load_data()
    
    # Initialize the embedding builder
    print("Initializing embedding model...")
    embedding_builder = SkillEmbeddingBuilder()
    
    # Generate and save student skill vectors
    print("\nGenerating student skill vectors...")
    student_vectors = embedding_builder.build_student_skill_vector(students_df)
    save_embeddings(student_vectors, 'student_skill_vectors')
    
    # Generate and save job skill vectors
    print("\nGenerating job skill vectors...")
    job_vectors = embedding_builder.build_job_skill_vector(jobs_df)
    save_embeddings(job_vectors, 'job_skill_vectors')
    
    # Generate and save course skill vectors
    print("\nGenerating course skill vectors...")
    course_vectors = embedding_builder.build_course_skill_vector(courses_df)
    save_embeddings(course_vectors, 'course_skill_vectors')
    
    # For student interests, we'll use a subset of student data
    if 'UserInterests' in students_df.columns and 'PreferredTrack' in students_df.columns:
        print("\nGenerating student interest vectors...")
        interest_vectors = embedding_builder.build_student_interest_vector(students_df)
        save_embeddings(interest_vectors, 'student_interest_vectors')
    
    print("\nAll embeddings generated and saved successfully!")
    print("You can find the embeddings in the 'embeddings' directory.")

if __name__ == "__main__":
    main()
