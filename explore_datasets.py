import pandas as pd
import numpy as np

print("="*80)
print("EXPLORING ALL THREE DATASETS")
print("="*80)

# 1. STUDENT DATASET
print("\n\n1. STUDENT DATASET")
print("-"*80)
try:
    df_students = pd.read_csv('digital_twin_students_1500_FINAL_CORRECTED (1).csv')
    print(f"Shape: {df_students.shape}")
    print(f"\nColumns ({len(df_students.columns)}):")
    for i, col in enumerate(df_students.columns, 1):
        print(f"  {i}. {col}")
    
    print(f"\nData Types Summary:")
    print(df_students.dtypes.value_counts())
    
    print(f"\nMissing Values (top 10):")
    missing = df_students.isnull().sum().sort_values(ascending=False).head(10)
    for col, count in missing.items():
        pct = (count / len(df_students)) * 100
        print(f"  {col}: {count} ({pct:.1f}%)")
    
    print(f"\nDuplicates: {df_students.duplicated().sum()}")
    
    # Check for grade columns
    grade_cols = [col for col in df_students.columns if 'Grade' in col or 'grade' in col]
    print(f"\nGrade Columns ({len(grade_cols)}):")
    for col in grade_cols[:5]:
        print(f"  {col}: {df_students[col].unique()[:10]}")
    
except Exception as e:
    print(f"Error loading student dataset: {e}")

# 2. COURSES DATASET
print("\n\n2. COURSES DATASET")
print("-"*80)
try:
    df_courses = pd.read_csv('digital_twin_courses_1500.csv')
    print(f"Shape: {df_courses.shape}")
    print(f"\nColumns:")
    for i, col in enumerate(df_courses.columns, 1):
        print(f"  {i}. {col}")
    
    print(f"\nFirst 3 rows:")
    print(df_courses.head(3))
    
    print(f"\nDuplicates: {df_courses.duplicated().sum()}")
    
except Exception as e:
    print(f"Error loading courses dataset: {e}")

# 3. JOBS DATASET
print("\n\n3. JOBS DATASET")
print("-"*80)
try:
    df_jobs = pd.read_csv('egypt_jobs_full_1500.csv', on_bad_lines='skip')
    print(f"Shape: {df_jobs.shape}")
    print(f"\nColumns:")
    for i, col in enumerate(df_jobs.columns, 1):
        print(f"  {i}. {col}")
    
    print(f"\nFirst 2 rows:")
    for col in df_jobs.columns:
        print(f"  {col}: {df_jobs[col].iloc[0]}")
    
    print(f"\nDuplicates: {df_jobs.duplicated().sum()}")
    
except Exception as e:
    print(f"Error loading jobs dataset: {e}")

print("\n" + "="*80)
print("EXPLORATION COMPLETE")
print("="*80)
