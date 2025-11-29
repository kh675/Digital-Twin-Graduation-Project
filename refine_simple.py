"""
Simple Refinement Script - Students Dataset
Fixes: PrevTraining, ExternalCourses, PreferredTrack
"""

import pandas as pd
import sys

# Increase field size limit
import csv
csv.field_size_limit(sys.maxsize)

INPUT_FILE = 'digital_twin_students_1500_FINAL_CORRECTED (1).csv'
OUTPUT_FILE = 'students_1500_PRODUCTION_READY.csv'

def fix_prev_training(value):
    """Merge tokenized PrevTraining back together"""
    if pd.isna(value) or value == '':
        return ''
    value = str(value).strip()
    parts = [p.strip() for p in value.split(';') if p.strip()]
    if not parts:
        return ''
    return ' '.join(parts)

def fix_external_courses(value):
    """Merge provider names like 'AWS; Academy' -> 'AWS Academy'"""
    if pd.isna(value) or value == '':
        return ''
    value = str(value).strip()
    parts = [p.strip() for p in value.split(';') if p.strip()]
    if not parts:
        return ''
    
    # Merge consecutive parts if they form known providers
    merged = []
    i = 0
    while i < len(parts):
        if i < len(parts) - 1:
            combined = f"{parts[i]} {parts[i+1]}"
            # Check if it's a known provider pattern
            if any(x in combined.lower() for x in ['aws academy', 'google cloud', 'microsoft learn', 'ibm skills']):
                merged.append(combined)
                i += 2
                continue
        merged.append(parts[i])
        i += 1
    
    return '; '.join(merged)

def standardize_track(track):
    """Standardize PreferredTrack labels"""
    if pd.isna(track) or track == '':
        return 'Software Engineer'
    
    track = str(track).strip().lower()
    
    # Mapping dictionary
    mapping = {
        'ml engineer': 'ML Engineer', 'machine learning engineer': 'ML Engineer', 'machine learning': 'ML Engineer',
        'ai engineer': 'AI Engineer', 'artificial intelligence engineer': 'AI Engineer',
        'data scientist': 'Data Scientist', 'data science': 'Data Scientist',
        'data engineer': 'Data Engineer', 'data engineering': 'Data Engineer',
        'cloud engineer': 'Cloud Engineer', 'cloud': 'Cloud Engineer',
        'full stack': 'Full Stack Developer', 'full stack developer': 'Full Stack Developer', 
        'fullstack': 'Full Stack Developer', 'full-stack': 'Full Stack Developer',
        'frontend': 'Frontend Developer', 'frontend developer': 'Frontend Developer',
        'front-end': 'Frontend Developer', 'front end': 'Frontend Developer',
        'backend': 'Backend Developer', 'backend developer': 'Backend Developer',
        'back-end': 'Backend Developer', 'back end': 'Backend Developer',
        'mobile': 'Mobile Developer', 'mobile developer': 'Mobile Developer',
        'devops': 'DevOps Engineer', 'devops engineer': 'DevOps Engineer', 'dev ops': 'DevOps Engineer',
        'cybersecurity': 'Security Engineer', 'security': 'Security Engineer', 'security engineer': 'Security Engineer',
        'software engineer': 'Software Engineer', 'software developer': 'Software Engineer',
        'qa engineer': 'QA Engineer', 'qa': 'QA Engineer', 'quality assurance': 'QA Engineer'
    }
    
    return mapping.get(track, track.title())

print("="*80)
print(" FINAL REFINEMENT - STUDENTS DATASET")
print("="*80)

print("\nLoading dataset...")
df = pd.read_csv(INPUT_FILE, low_memory=False)
print(f"Loaded {len(df)} records with {len(df.columns)} columns")

print("\n1. Fixing PrevTraining...")
if 'PrevTraining' in df.columns:
    df['PrevTraining'] = df['PrevTraining'].apply(fix_prev_training)
    print(f"   ✓ Fixed {len(df)} records")
    print(f"   Sample: {df['PrevTraining'].iloc[0][:80]}...")

print("\n2. Fixing ExternalCourses...")
if 'ExternalCourses' in df.columns:
    df['ExternalCourses'] = df['ExternalCourses'].apply(fix_external_courses)
    print(f"   ✓ Fixed {len(df)} records")
    print(f"   Sample: {df['ExternalCourses'].iloc[1][:80] if len(df) > 1 else 'N/A'}...")

print("\n3. Standardizing PreferredTrack...")
if 'PreferredTrack' in df.columns:
    before = df['PreferredTrack'].nunique()
    df['PreferredTrack'] = df['PreferredTrack'].apply(standardize_track)
    after = df['PreferredTrack'].nunique()
    print(f"   ✓ Reduced from {before} to {after} unique values")
    print(f"\n   Top tracks:")
    for track, count in df['PreferredTrack'].value_counts().head(10).items():
        print(f"      {track}: {count}")

print("\n4. Verifying critical columns...")
critical = ['StudentID', 'Department', 'GPA', 'AttendancePercent', 'PreferredTrack', 'UserInterests']
for col in critical:
    if col in df.columns:
        missing = df[col].isnull().sum()
        if missing > 0:
            print(f"   ⚠ {col}: {missing} missing - filling...")
            if col == 'PreferredTrack':
                df[col] = df[col].fillna('Software Engineer')
            elif col == 'UserInterests':
                df[col] = df[col].fillna('General Technology')
            elif col in ['GPA', 'AttendancePercent']:
                df[col] = df[col].fillna(df[col].median())
        else:
            print(f"   ✓ {col}: complete")

print(f"\nSaving to {OUTPUT_FILE}...")
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

print("\n" + "="*80)
print(" REFINEMENT COMPLETED")
print("="*80)
print(f"✓ Saved to: {OUTPUT_FILE}")
print(f"✓ {len(df)} records, {len(df.columns)} columns")
print(f"✓ Missing values: {df.isnull().sum().sum()}")
print("\nDataset is now PRODUCTION-READY!")
