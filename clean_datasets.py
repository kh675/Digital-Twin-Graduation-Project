"""
Data Cleaning Script for Digital Twin AI Project
Cleans and prepares three datasets: courses, students, and jobs data
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

# Configuration
DATASETS = {
    'courses': 'digital_twin_courses_1500.csv',
    'students': 'digital_twin_students_1500_FINAL_CORRECTED (1).csv',
    'jobs': 'egypt_jobs_full_1500.csv'
}

OUTPUT_SUFFIX = '_cleaned.csv'
REPORT_FILE = 'data_quality_report.txt'

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")

def clean_text(text):
    """Clean and standardize text fields"""
    if pd.isna(text):
        return text
    
    # Convert to string
    text = str(text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep important punctuation
    text = re.sub(r'[^\w\s,.\-()&/]', '', text)
    
    return text.strip()

def standardize_skills(skills_text):
    """Standardize skill lists"""
    if pd.isna(skills_text):
        return skills_text
    
    skills_text = str(skills_text)
    
    # Split by common delimiters
    skills = re.split(r'[,;|]', skills_text)
    
    # Clean each skill
    skills = [clean_text(skill).title() for skill in skills if skill.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in skills:
        if skill.lower() not in seen:
            seen.add(skill.lower())
            unique_skills.append(skill)
    
    return ', '.join(unique_skills)

def clean_courses_dataset(df):
    """Clean the courses dataset"""
    print_section("Cleaning Courses Dataset")
    
    original_shape = df.shape
    print(f"Original shape: {original_shape}")
    print(f"Original duplicates: {df.duplicated().sum()}")
    
    # Remove duplicates
    df = df.drop_duplicates()
    print(f"After removing duplicates: {df.shape}")
    print(f"Duplicates removed: {original_shape[0] - df.shape[0]}")
    
    # Clean text columns
    text_columns = ['CourseProvider', 'CourseTitle', 'Description', 'Department', 'Track']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
    
    # Standardize skills
    if 'SkillsGained' in df.columns:
        df['SkillsGained'] = df['SkillsGained'].apply(standardize_skills)
    
    # Standardize level values
    if 'Level' in df.columns:
        level_mapping = {
            'beginner': 'Beginner',
            'intermediate': 'Intermediate',
            'advanced': 'Advanced',
            'expert': 'Expert'
        }
        df['Level'] = df['Level'].str.strip().str.lower().map(
            lambda x: level_mapping.get(x, x.title() if pd.notna(x) else x)
        )
    
    print(f"\nFinal shape: {df.shape}")
    print(f"Missing values:\n{df.isnull().sum()}")
    
    return df

def clean_students_dataset(df):
    """Clean the students dataset"""
    print_section("Cleaning Students Dataset")
    
    original_shape = df.shape
    print(f"Original shape: {original_shape}")
    print(f"Original missing values: {df.isnull().sum().sum()}")
    
    # Identify numeric and categorical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Remove StudentID from categorical if present
    if 'StudentID' in categorical_cols:
        categorical_cols.remove('StudentID')
    
    print(f"\nNumeric columns: {len(numeric_cols)}")
    print(f"Categorical columns: {len(categorical_cols)}")
    
    # Handle missing values in numeric columns (use median)
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"Filled {col} with median: {median_val}")
    
    # Handle missing values in categorical columns
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            # Try mode first
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col].fillna(mode_val[0], inplace=True)
                print(f"Filled {col} with mode: {mode_val[0]}")
            else:
                df[col].fillna('Unknown', inplace=True)
                print(f"Filled {col} with 'Unknown'")
    
    # Clean text in categorical columns
    for col in categorical_cols:
        df[col] = df[col].apply(clean_text)
    
    # Standardize StudentID format if present
    if 'StudentID' in df.columns:
        df['StudentID'] = df['StudentID'].apply(lambda x: str(x).strip() if pd.notna(x) else x)
    
    print(f"\nFinal shape: {df.shape}")
    print(f"Remaining missing values: {df.isnull().sum().sum()}")
    
    return df

def clean_jobs_dataset(df):
    """Clean the jobs dataset"""
    print_section("Cleaning Jobs Dataset")
    
    original_shape = df.shape
    print(f"Original shape: {original_shape}")
    print(f"Original missing values: {df.isnull().sum().sum()}")
    
    # Clean text columns
    text_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    # Remove job_id from text columns if present
    if 'job_id' in text_columns:
        text_columns.remove('job_id')
    
    for col in text_columns:
        if col in df.columns:
            # Special handling for skills columns
            if 'skill' in col.lower() or 'requirement' in col.lower():
                df[col] = df[col].apply(standardize_skills)
            else:
                df[col] = df[col].apply(clean_text)
    
    # Standardize job titles and company names
    if 'job_title' in df.columns:
        df['job_title'] = df['job_title'].str.title()
    
    if 'company' in df.columns or 'company_name' in df.columns:
        company_col = 'company' if 'company' in df.columns else 'company_name'
        df[company_col] = df[company_col].str.title()
    
    # Clean location field
    location_cols = [col for col in df.columns if 'location' in col.lower() or 'city' in col.lower()]
    for col in location_cols:
        df[col] = df[col].str.title()
    
    print(f"\nFinal shape: {df.shape}")
    print(f"Missing values:\n{df.isnull().sum()}")
    
    return df

def generate_quality_report(original_stats, cleaned_stats, output_file):
    """Generate a comprehensive data quality report"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("DATA QUALITY REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        for dataset_name in ['courses', 'students', 'jobs']:
            f.write(f"\n{dataset_name.upper()} DATASET\n")
            f.write("-"*80 + "\n\n")
            
            orig = original_stats[dataset_name]
            clean = cleaned_stats[dataset_name]
            
            f.write("BEFORE CLEANING:\n")
            f.write(f"  Rows: {orig['rows']}\n")
            f.write(f"  Columns: {orig['columns']}\n")
            f.write(f"  Duplicates: {orig['duplicates']}\n")
            f.write(f"  Missing values: {orig['missing']}\n\n")
            
            f.write("AFTER CLEANING:\n")
            f.write(f"  Rows: {clean['rows']}\n")
            f.write(f"  Columns: {clean['columns']}\n")
            f.write(f"  Duplicates: {clean['duplicates']}\n")
            f.write(f"  Missing values: {clean['missing']}\n\n")
            
            f.write("CHANGES:\n")
            f.write(f"  Rows removed: {orig['rows'] - clean['rows']}\n")
            f.write(f"  Duplicates removed: {orig['duplicates'] - clean['duplicates']}\n")
            f.write(f"  Missing values handled: {orig['missing'] - clean['missing']}\n\n")
            
            # Calculate quality score (0-100)
            quality_score = 100
            if clean['duplicates'] > 0:
                quality_score -= 10
            if clean['missing'] > 0:
                quality_score -= (clean['missing'] / (clean['rows'] * clean['columns'])) * 30
            
            f.write(f"  Data Quality Score: {quality_score:.2f}/100\n")
            f.write("\n" + "="*80 + "\n")

def main():
    """Main execution function"""
    print_section("DATA CLEANING SCRIPT - DIGITAL TWIN AI PROJECT")
    
    original_stats = {}
    cleaned_stats = {}
    
    # Clean Courses Dataset
    print("\n[1/3] Processing Courses Dataset...")
    df_courses = pd.read_csv(DATASETS['courses'])
    original_stats['courses'] = {
        'rows': df_courses.shape[0],
        'columns': df_courses.shape[1],
        'duplicates': df_courses.duplicated().sum(),
        'missing': df_courses.isnull().sum().sum()
    }
    
    df_courses_clean = clean_courses_dataset(df_courses)
    output_file = DATASETS['courses'].replace('.csv', OUTPUT_SUFFIX)
    df_courses_clean.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Saved to: {output_file}")
    
    cleaned_stats['courses'] = {
        'rows': df_courses_clean.shape[0],
        'columns': df_courses_clean.shape[1],
        'duplicates': df_courses_clean.duplicated().sum(),
        'missing': df_courses_clean.isnull().sum().sum()
    }
    
    # Clean Students Dataset
    print("\n[2/3] Processing Students Dataset...")
    df_students = pd.read_csv(DATASETS['students'], low_memory=False)
    original_stats['students'] = {
        'rows': df_students.shape[0],
        'columns': df_students.shape[1],
        'duplicates': df_students.duplicated().sum(),
        'missing': df_students.isnull().sum().sum()
    }
    
    df_students_clean = clean_students_dataset(df_students)
    output_file = 'digital_twin_students_1500_cleaned.csv'
    df_students_clean.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Saved to: {output_file}")
    
    cleaned_stats['students'] = {
        'rows': df_students_clean.shape[0],
        'columns': df_students_clean.shape[1],
        'duplicates': df_students_clean.duplicated().sum(),
        'missing': df_students_clean.isnull().sum().sum()
    }
    
    # Clean Jobs Dataset
    print("\n[3/3] Processing Jobs Dataset...")
    df_jobs = pd.read_csv(DATASETS['jobs'])
    original_stats['jobs'] = {
        'rows': df_jobs.shape[0],
        'columns': df_jobs.shape[1],
        'duplicates': df_jobs.duplicated().sum(),
        'missing': df_jobs.isnull().sum().sum()
    }
    
    df_jobs_clean = clean_jobs_dataset(df_jobs)
    output_file = DATASETS['jobs'].replace('.csv', OUTPUT_SUFFIX)
    df_jobs_clean.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Saved to: {output_file}")
    
    cleaned_stats['jobs'] = {
        'rows': df_jobs_clean.shape[0],
        'columns': df_jobs_clean.shape[1],
        'duplicates': df_jobs_clean.duplicated().sum(),
        'missing': df_jobs_clean.isnull().sum().sum()
    }
    
    # Generate quality report
    print_section("Generating Data Quality Report")
    generate_quality_report(original_stats, cleaned_stats, REPORT_FILE)
    print(f"✓ Quality report saved to: {REPORT_FILE}")
    
    print_section("DATA CLEANING COMPLETED SUCCESSFULLY")
    print("Summary:")
    print(f"  ✓ Courses dataset: {original_stats['courses']['rows']} → {cleaned_stats['courses']['rows']} rows")
    print(f"  ✓ Students dataset: {original_stats['students']['rows']} → {cleaned_stats['students']['rows']} rows")
    print(f"  ✓ Jobs dataset: {original_stats['jobs']['rows']} → {cleaned_stats['jobs']['rows']} rows")
    print(f"\nAll cleaned datasets saved with '{OUTPUT_SUFFIX}' suffix")
    print(f"Quality report: {REPORT_FILE}\n")

if __name__ == "__main__":
    main()
