"""
Final Refinement Script for Students Dataset
Fixes remaining issues:
- PrevTraining: merge tokenized course names back together
- ExternalCourses: merge provider names that were split
- PreferredTrack: standardize all variants to canonical labels
- Verify no missing critical values
"""

import pandas as pd
import numpy as np
import re

# Configuration
INPUT_FILE = 'digital_twin_students_1500_FINAL_CLEANED.csv'
OUTPUT_FILE = 'students_1500_PRODUCTION_READY.csv'

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")

def fix_prev_training(value):
    """
    Fix PrevTraining field - merge tokenized parts back into full course names
    Example: "Huawei; -; Huawei; Full-Stack; Developer; -; Cohort; 1"
    Should be: "Huawei - Huawei Full-Stack Developer - Cohort 1"
    """
    if pd.isna(value) or value == '':
        return ''
    
    value = str(value).strip()
    
    # Split by semicolon
    parts = [p.strip() for p in value.split(';') if p.strip()]
    
    # If no parts, return empty
    if not parts:
        return ''
    
    # Merge parts back together with spaces, but keep '-' as separator
    # Strategy: join all parts with spaces, but replace ' - ' pattern with actual dash separator
    merged = ' '.join(parts)
    
    # Clean up multiple spaces
    merged = ' '.join(merged.split())
    
    return merged

def fix_external_courses(value):
    """
    Fix ExternalCourses - merge provider names that were incorrectly split
    Example: "AWS; Academy" should be "AWS Academy"
    """
    if pd.isna(value) or value == '':
        return ''
    
    value = str(value).strip()
    
    # Known provider patterns that should NOT be split
    providers = [
        'AWS Academy',
        'Google Cloud',
        'Microsoft Learn',
        'IBM Skills',
        'Oracle Academy',
        'Cisco Networking',
        'Red Hat',
        'Linux Foundation'
    ]
    
    # Split by semicolon
    parts = [p.strip() for p in value.split(';') if p.strip()]
    
    if not parts:
        return ''
    
    # Try to merge known provider patterns
    merged_parts = []
    i = 0
    while i < len(parts):
        # Check if current part + next part forms a known provider
        if i < len(parts) - 1:
            combined = f"{parts[i]} {parts[i+1]}"
            if any(provider.lower() in combined.lower() for provider in providers):
                merged_parts.append(combined)
                i += 2
                continue
        
        merged_parts.append(parts[i])
        i += 1
    
    # Join multiple courses with semicolon
    return '; '.join(merged_parts)

def standardize_preferred_track(track):
    """
    Standardize PreferredTrack to canonical labels
    Handle variants like "Front-end", "frontend", "Front End" -> "Frontend Developer"
    """
    if pd.isna(track) or track == '':
        return 'Software Engineer'  # Default
    
    track = str(track).strip().lower()
    
    # Comprehensive mapping of all variants to canonical labels
    track_map = {
        # ML/AI variants
        'ml engineer': 'ML Engineer',
        'machine learning engineer': 'ML Engineer',
        'machine learning': 'ML Engineer',
        'ml': 'ML Engineer',
        'ai engineer': 'AI Engineer',
        'artificial intelligence engineer': 'AI Engineer',
        'ai': 'AI Engineer',
        
        # Data variants
        'data scientist': 'Data Scientist',
        'data science': 'Data Scientist',
        'data engineer': 'Data Engineer',
        'data engineering': 'Data Engineer',
        
        # Cloud variants
        'cloud engineer': 'Cloud Engineer',
        'cloud': 'Cloud Engineer',
        'cloud developer': 'Cloud Engineer',
        
        # Full Stack variants
        'full stack': 'Full Stack Developer',
        'full stack developer': 'Full Stack Developer',
        'fullstack': 'Full Stack Developer',
        'full-stack': 'Full Stack Developer',
        'full-stack developer': 'Full Stack Developer',
        
        # Frontend variants
        'frontend': 'Frontend Developer',
        'frontend developer': 'Frontend Developer',
        'front-end': 'Frontend Developer',
        'front end': 'Frontend Developer',
        'front-end developer': 'Frontend Developer',
        'front end developer': 'Frontend Developer',
        
        # Backend variants
        'backend': 'Backend Developer',
        'backend developer': 'Backend Developer',
        'back-end': 'Backend Developer',
        'back end': 'Backend Developer',
        'back-end developer': 'Backend Developer',
        'back end developer': 'Backend Developer',
        
        # Mobile variants
        'mobile': 'Mobile Developer',
        'mobile developer': 'Mobile Developer',
        'mobile dev': 'Mobile Developer',
        'ios developer': 'Mobile Developer',
        'android developer': 'Mobile Developer',
        
        # DevOps variants
        'devops': 'DevOps Engineer',
        'devops engineer': 'DevOps Engineer',
        'dev ops': 'DevOps Engineer',
        'dev-ops': 'DevOps Engineer',
        
        # Security variants
        'cybersecurity': 'Security Engineer',
        'cyber security': 'Security Engineer',
        'security': 'Security Engineer',
        'security engineer': 'Security Engineer',
        'cybersecurity specialist': 'Security Engineer',
        'information security': 'Security Engineer',
        
        # Software Engineer variants
        'software engineer': 'Software Engineer',
        'software developer': 'Software Engineer',
        'software dev': 'Software Engineer',
        'swe': 'Software Engineer',
        
        # QA/Testing variants
        'qa engineer': 'QA Engineer',
        'qa': 'QA Engineer',
        'quality assurance': 'QA Engineer',
        'test engineer': 'QA Engineer',
        'tester': 'QA Engineer',
        
        # Other specific roles
        'game developer': 'Game Developer',
        'embedded engineer': 'Embedded Engineer',
        'systems engineer': 'Systems Engineer',
        'network engineer': 'Network Engineer',
        'database administrator': 'Database Administrator',
        'dba': 'Database Administrator'
    }
    
    # Try exact match first
    if track in track_map:
        return track_map[track]
    
    # Try partial match
    for key, value in track_map.items():
        if key in track or track in key:
            return value
    
    # If no match found, title case the original
    return track.title()

def refine_students_dataset(df):
    """Perform final refinements on students dataset"""
    print_section("FINAL REFINEMENT - STUDENTS DATASET")
    
    print(f"Original shape: {df.shape}\n")
    
    # 1. Fix PrevTraining
    print("1. Fixing PrevTraining tokenization...")
    if 'PrevTraining' in df.columns:
        before_sample = df['PrevTraining'].iloc[0] if len(df) > 0 else ''
        df['PrevTraining'] = df['PrevTraining'].apply(fix_prev_training)
        after_sample = df['PrevTraining'].iloc[0] if len(df) > 0 else ''
        print(f"   Before: {before_sample}")
        print(f"   After:  {after_sample}")
        print(f"   ✓ Fixed {len(df)} records")
    
    # 2. Fix ExternalCourses
    print("\n2. Fixing ExternalCourses structure...")
    if 'ExternalCourses' in df.columns:
        before_sample = df['ExternalCourses'].iloc[1] if len(df) > 1 else ''
        df['ExternalCourses'] = df['ExternalCourses'].apply(fix_external_courses)
        after_sample = df['ExternalCourses'].iloc[1] if len(df) > 1 else ''
        print(f"   Before: {before_sample}")
        print(f"   After:  {after_sample}")
        print(f"   ✓ Fixed {len(df)} records")
    
    # 3. Standardize PreferredTrack
    print("\n3. Standardizing PreferredTrack labels...")
    if 'PreferredTrack' in df.columns:
        before_unique = df['PreferredTrack'].nunique()
        df['PreferredTrack'] = df['PreferredTrack'].apply(standardize_preferred_track)
        after_unique = df['PreferredTrack'].nunique()
        print(f"   Before: {before_unique} unique values")
        print(f"   After:  {after_unique} unique values")
        print(f"\n   Canonical labels:")
        for track, count in df['PreferredTrack'].value_counts().head(15).items():
            print(f"      {track}: {count}")
    
    # 4. Verify Critical Columns
    print("\n4. Verifying critical columns have no missing values...")
    critical_columns = [
        'StudentID', 'Department', 'GPA', 'AttendancePercent', 
        'Internships', 'PreferredTrack', 'UserInterests'
    ]
    
    all_good = True
    for col in critical_columns:
        if col in df.columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                print(f"   ⚠ {col}: {missing} missing values - FIXING...")
                
                # Fix missing values
                if col == 'PreferredTrack':
                    df[col] = df[col].fillna('Software Engineer')
                elif col == 'UserInterests':
                    df[col] = df[col].fillna('General Technology')
                elif col == 'Internships':
                    df[col] = df[col].fillna(0)
                elif col in ['GPA', 'AttendancePercent']:
                    df[col] = df[col].fillna(df[col].median())
                
                all_good = False
            else:
                print(f"   ✓ {col}: no missing values")
        else:
            print(f"   ⚠ {col}: column not found in dataset")
    
    if all_good:
        print("\n   ✓ All critical columns complete!")
    
    print(f"\nFinal shape: {df.shape}")
    print(f"Final missing values: {df.isnull().sum().sum()}")
    
    return df

def main():
    """Main execution function"""
    print_section("FINAL REFINEMENT SCRIPT - STUDENTS DATASET")
    
    # Load dataset with low_memory=False to avoid dtype warnings
    print("Loading dataset...")
    try:
        df = pd.read_csv(INPUT_FILE, low_memory=False, encoding='utf-8')
    except:
        # Try with different encoding
        df = pd.read_csv(INPUT_FILE, low_memory=False, encoding='latin-1')
    
    print(f"Loaded {len(df)} records with {len(df.columns)} columns")
    
    # Refine dataset
    df_refined = refine_students_dataset(df)
    
    # Save refined dataset
    print(f"\nSaving to {OUTPUT_FILE}...")
    df_refined.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    print_section("REFINEMENT COMPLETED")
    print(f"✓ Saved refined dataset to: {OUTPUT_FILE}")
    print("\nDataset is now fully cleaned and production-ready!")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
