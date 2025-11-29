"""
Deep Data Cleaning Script for Digital Twin AI Project
Addresses specific issues found in user review:
- Fix email format (missing @)
- Restore separators in multi-valued columns
- Standardize categorical values
- Validate numeric ranges
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

# Configuration
STUDENTS_ORIGINAL = 'digital_twin_students_1500_FINAL_CORRECTED (1).csv'
STUDENTS_OUTPUT = 'digital_twin_students_1500_FINAL_CLEANED.csv'
COURSES_FILE = 'digital_twin_courses_1500_cleaned.csv'
JOBS_FILE = 'egypt_jobs_full_1500_cleaned.csv'

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")

def fix_email(email):
    """Fix email format - add missing @ symbol"""
    if pd.isna(email):
        return email
    
    email = str(email).strip()
    
    # If email doesn't contain @, add it before uni.edu.eg
    if '@' not in email:
        email = email.replace('uni.edu.eg', '@uni.edu.eg')
    
    return email

def validate_email(email):
    """Validate email format"""
    if pd.isna(email):
        return False
    
    email = str(email)
    # Should have exactly one @, and end with uni.edu.eg
    return email.count('@') == 1 and email.endswith('uni.edu.eg')

def normalize_multi_value_field(value, separator=';'):
    """
    Normalize multi-valued fields to use consistent separator
    Handles various input formats: comma-separated, space-separated, or concatenated
    """
    if pd.isna(value) or value == '':
        return ''
    
    value = str(value).strip()
    
    # If already has semicolons, clean and return
    if ';' in value:
        items = [item.strip() for item in value.split(';') if item.strip()]
        return f'{separator} '.join(items)
    
    # If has commas, split on commas
    if ',' in value:
        items = [item.strip() for item in value.split(',') if item.strip()]
        return f'{separator} '.join(items)
    
    # Try to split concatenated words using capital letters
    # e.g., "PythonDockerKubernetes" -> "Python Docker Kubernetes"
    # Look for patterns like lowercase followed by uppercase
    if value and not ' ' in value and any(c.isupper() for c in value[1:]):
        # Insert space before capital letters (except first char)
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', value)
        # Also handle acronyms and multi-word patterns
        spaced = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', spaced)
        items = [item.strip() for item in spaced.split() if item.strip()]
        return f'{separator} '.join(items)
    
    # If has spaces, assume already separated
    if ' ' in value:
        items = [item.strip() for item in value.split() if item.strip()]
        return f'{separator} '.join(items)
    
    # Single item
    return value.strip()

def standardize_department(dept):
    """Standardize department values"""
    if pd.isna(dept):
        return dept
    
    dept = str(dept).strip().upper()
    
    # Map variations to standard values
    dept_map = {
        'CS': 'CS',
        'COMPUTER SCIENCE': 'CS',
        'AI': 'AI',
        'ARTIFICIAL INTELLIGENCE': 'AI',
        'IS': 'IS',
        'INFORMATION SYSTEMS': 'IS',
        'NETWORK': 'Network',
        'NETWORKING': 'Network',
        'NET': 'Network'
    }
    
    return dept_map.get(dept, dept)

def standardize_track(track):
    """Standardize track/career path values"""
    if pd.isna(track) or track == '':
        return track
    
    track = str(track).strip()
    
    # Common variations mapping
    track_map = {
        'ml engineer': 'ML Engineer',
        'machine learning engineer': 'ML Engineer',
        'cloud engineer': 'Cloud Engineer',
        'cloud': 'Cloud Engineer',
        'full stack': 'Full Stack Developer',
        'full stack developer': 'Full Stack Developer',
        'fullstack': 'Full Stack Developer',
        'devops': 'DevOps Engineer',
        'devops engineer': 'DevOps Engineer',
        'data scientist': 'Data Scientist',
        'data science': 'Data Scientist',
        'backend': 'Backend Developer',
        'backend developer': 'Backend Developer',
        'frontend': 'Frontend Developer',
        'frontend developer': 'Frontend Developer',
        'mobile': 'Mobile Developer',
        'mobile developer': 'Mobile Developer',
        'cybersecurity': 'Cybersecurity Specialist',
        'security': 'Cybersecurity Specialist',
        'data engineer': 'Data Engineer',
        'ai engineer': 'AI Engineer',
        'software engineer': 'Software Engineer'
    }
    
    track_lower = track.lower().strip()
    return track_map.get(track_lower, track.title())

def standardize_communication_method(method):
    """Standardize communication method values"""
    if pd.isna(method):
        return method
    
    method = str(method).strip().lower()
    
    method_map = {
        'email': 'Email',
        'e-mail': 'Email',
        'sms': 'SMS',
        'text': 'SMS',
        'whatsapp': 'WhatsApp',
        'whats app': 'WhatsApp',
        'in-person': 'In-Person',
        'in person': 'In-Person',
        'face to face': 'In-Person',
        'video call': 'Video Call',
        'video': 'Video Call',
        'zoom': 'Video Call',
        'phone': 'Phone',
        'call': 'Phone'
    }
    
    return method_map.get(method, method.title())

def validate_and_fix_numeric(value, min_val, max_val, default=None):
    """Validate numeric value is within range"""
    try:
        val = float(value)
        if min_val <= val <= max_val:
            return val
        else:
            return default if default is not None else min_val
    except (ValueError, TypeError):
        return default if default is not None else min_val

def deep_clean_students_dataset(df):
    """Perform deep cleaning on students dataset"""
    print_section("DEEP CLEANING STUDENTS DATASET")
    
    print(f"Original shape: {df.shape}")
    print(f"Original missing values: {df.isnull().sum().sum()}\n")
    
    # 1. Fix Email Format
    print("1. Fixing email format...")
    if 'Email' in df.columns:
        df['Email'] = df['Email'].apply(fix_email)
        valid_emails = df['Email'].apply(validate_email).sum()
        print(f"   ✓ Fixed emails: {valid_emails}/{len(df)} valid")
    
    # 2. Normalize Multi-Value Fields
    print("\n2. Normalizing multi-value fields with semicolon separator...")
    multi_value_columns = [
        'Skills', 'Extracurriculars', 'PrevTraining', 'Projects', 
        'CoursesCompleted', 'TechnicalSkills', 'SoftSkills', 
        'ExternalCourses', 'Activities', 'UserInterests'
    ]
    
    for col in multi_value_columns:
        if col in df.columns:
            before_sample = df[col].iloc[0] if len(df) > 0 else ''
            df[col] = df[col].apply(normalize_multi_value_field)
            after_sample = df[col].iloc[0] if len(df) > 0 else ''
            print(f"   ✓ {col}")
            if before_sample != after_sample:
                print(f"     Before: {str(before_sample)[:50]}...")
                print(f"     After:  {str(after_sample)[:50]}...")
    
    # 3. Standardize Categorical Values
    print("\n3. Standardizing categorical values...")
    
    if 'Department' in df.columns:
        df['Department'] = df['Department'].apply(standardize_department)
        print(f"   ✓ Department: {df['Department'].unique()}")
    
    if 'PreferredTrack' in df.columns:
        df['PreferredTrack'] = df['PreferredTrack'].apply(standardize_track)
        print(f"   ✓ PreferredTrack: {df['PreferredTrack'].nunique()} unique values")
    
    if 'PreferredCommunicationMethod' in df.columns:
        df['PreferredCommunicationMethod'] = df['PreferredCommunicationMethod'].apply(standardize_communication_method)
        print(f"   ✓ PreferredCommunicationMethod: {df['PreferredCommunicationMethod'].unique()}")
    
    # 4. Validate Numeric Ranges
    print("\n4. Validating numeric ranges...")
    
    if 'GPA' in df.columns:
        df['GPA'] = df['GPA'].apply(lambda x: validate_and_fix_numeric(x, 0, 4, default=2.0))
        print(f"   ✓ GPA: range [{df['GPA'].min():.2f}, {df['GPA'].max():.2f}]")
    
    if 'AttendancePercent' in df.columns:
        df['AttendancePercent'] = df['AttendancePercent'].apply(lambda x: validate_and_fix_numeric(x, 0, 100, default=75))
        print(f"   ✓ AttendancePercent: range [{df['AttendancePercent'].min():.1f}, {df['AttendancePercent'].max():.1f}]")
    
    if 'FailedCourses' in df.columns:
        df['FailedCourses'] = df['FailedCourses'].apply(lambda x: int(validate_and_fix_numeric(x, 0, 20, default=0)))
        print(f"   ✓ FailedCourses: range [{df['FailedCourses'].min()}, {df['FailedCourses'].max()}]")
    
    # 5. Handle Missing Critical Fields
    print("\n5. Checking critical fields...")
    critical_fields = ['StudentID', 'Department', 'GPA', 'AttendancePercent', 'PreferredTrack', 'UserInterests']
    
    for field in critical_fields:
        if field in df.columns:
            missing = df[field].isnull().sum()
            if missing > 0:
                print(f"   ⚠ {field}: {missing} missing values")
                
                # Handle missing values
                if field == 'PreferredTrack':
                    # Fill with most common track in same department
                    if 'Department' in df.columns:
                        df[field] = df.groupby('Department')[field].transform(
                            lambda x: x.fillna(x.mode()[0] if len(x.mode()) > 0 else 'Software Engineer')
                        )
                elif field == 'UserInterests':
                    df[field] = df[field].fillna('General Technology')
                elif field in ['GPA', 'AttendancePercent']:
                    df[field] = df[field].fillna(df[field].median())
            else:
                print(f"   ✓ {field}: no missing values")
    
    print(f"\nFinal shape: {df.shape}")
    print(f"Final missing values: {df.isnull().sum().sum()}")
    
    return df

def validate_jobs_dataset(df):
    """Validate jobs dataset"""
    print_section("VALIDATING JOBS DATASET")
    
    print(f"Shape: {df.shape}")
    
    critical_fields = ['job_id', 'job_title', 'company', 'location', 'department', 'job_level', 'required_skills']
    
    for field in critical_fields:
        if field in df.columns:
            missing = df[field].isnull().sum()
            if missing > 0:
                print(f"   ⚠ {field}: {missing} missing values ({missing/len(df)*100:.1f}%)")
            else:
                print(f"   ✓ {field}: complete")
        else:
            print(f"   ✗ {field}: column not found")
    
    # Check job_level categories
    if 'job_level' in df.columns:
        print(f"\n   Job levels: {df['job_level'].unique()}")
    
    return df

def validate_courses_dataset(df):
    """Validate courses dataset"""
    print_section("VALIDATING COURSES DATASET")
    
    print(f"Shape: {df.shape}")
    
    critical_fields = ['CourseProvider', 'CourseTitle', 'Description', 'SkillsGained', 'Department', 'Level', 'Track']
    
    for field in critical_fields:
        if field in df.columns:
            missing = df[field].isnull().sum()
            if missing > 0:
                print(f"   ⚠ {field}: {missing} missing values")
            else:
                print(f"   ✓ {field}: complete")
        else:
            print(f"   ✗ {field}: column not found")
    
    # Check SkillsGained separator consistency
    if 'SkillsGained' in df.columns:
        sample = df['SkillsGained'].iloc[0] if len(df) > 0 else ''
        print(f"\n   SkillsGained sample: {str(sample)[:80]}...")
        print(f"   Separator used: comma (,)")
    
    return df

def main():
    """Main execution function"""
    print_section("DEEP DATA CLEANING - DIGITAL TWIN AI PROJECT")
    
    # 1. Deep Clean Students Dataset
    print("\n[1/3] Deep cleaning students dataset...")
    df_students = pd.read_csv(STUDENTS_ORIGINAL, low_memory=False)
    df_students_clean = deep_clean_students_dataset(df_students)
    df_students_clean.to_csv(STUDENTS_OUTPUT, index=False, encoding='utf-8')
    print(f"✓ Saved to: {STUDENTS_OUTPUT}")
    
    # 2. Validate Jobs Dataset
    print("\n[2/3] Validating jobs dataset...")
    df_jobs = pd.read_csv(JOBS_FILE)
    df_jobs = validate_jobs_dataset(df_jobs)
    
    # 3. Validate Courses Dataset
    print("\n[3/3] Validating courses dataset...")
    df_courses = pd.read_csv(COURSES_FILE)
    df_courses = validate_courses_dataset(df_courses)
    
    print_section("DEEP CLEANING COMPLETED")
    print("✓ Students dataset: deeply cleaned and validated")
    print("✓ Jobs dataset: validated")
    print("✓ Courses dataset: validated")
    print(f"\nAll datasets are now ready for AI model usage!\n")

if __name__ == "__main__":
    main()
