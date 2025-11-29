"""
Feature Engineering Script - Add Numeric Grade Features
Adds numeric columns derived from Grades_Prev_Years letter grades
Keeps original letter grades for interpretability
"""

import pandas as pd
import numpy as np

INPUT_FILE = 'students_1500_PRODUCTION_READY.csv'
OUTPUT_FILE = 'students_1500_PRODUCTION_READY.csv'

# Grade to GPA mapping
GRADE_TO_GPA = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'D-': 0.7,
    'F': 0.0
}

def parse_and_convert_grades(grades_str):
    """
    Parse letter grades and convert to numeric values
    Returns: mean, min, max of numeric grades
    """
    if pd.isna(grades_str) or grades_str == '':
        return np.nan, np.nan, np.nan
    
    # Split by comma
    grades = [g.strip() for g in str(grades_str).split(',') if g.strip()]
    
    if not grades:
        return np.nan, np.nan, np.nan
    
    # Convert to numeric
    numeric_grades = []
    for grade in grades:
        # Handle variations
        grade_clean = grade.strip().upper()
        
        # Map to GPA
        if grade_clean in GRADE_TO_GPA:
            numeric_grades.append(GRADE_TO_GPA[grade_clean])
        else:
            # Try without + or -
            base_grade = grade_clean.replace('+', '').replace('-', '')
            if base_grade in GRADE_TO_GPA:
                numeric_grades.append(GRADE_TO_GPA[base_grade])
    
    if not numeric_grades:
        return np.nan, np.nan, np.nan
    
    return np.mean(numeric_grades), np.min(numeric_grades), np.max(numeric_grades)

print("="*80)
print(" FEATURE ENGINEERING - NUMERIC GRADE FEATURES")
print("="*80)

print("\nLoading dataset...")
df = pd.read_csv(INPUT_FILE, low_memory=False)
print(f"Loaded {len(df)} records with {len(df.columns)} columns")

print("\nAdding numeric grade features from Grades_Prev_Years...")

if 'Grades_Prev_Years' in df.columns:
    # Show sample before
    print(f"\nSample Grades_Prev_Years (original):")
    print(df['Grades_Prev_Years'].head(3).tolist())
    
    # Apply conversion
    grade_stats = df['Grades_Prev_Years'].apply(parse_and_convert_grades)
    
    # Create new columns
    df['PrevYears_Grade_Mean'] = grade_stats.apply(lambda x: x[0])
    df['PrevYears_Grade_Min'] = grade_stats.apply(lambda x: x[1])
    df['PrevYears_Grade_Max'] = grade_stats.apply(lambda x: x[2])
    
    # Show results
    print(f"\n✓ Created 3 new numeric columns:")
    print(f"   - PrevYears_Grade_Mean")
    print(f"   - PrevYears_Grade_Min")
    print(f"   - PrevYears_Grade_Max")
    
    print(f"\nSample numeric values:")
    sample_df = df[['Grades_Prev_Years', 'PrevYears_Grade_Mean', 'PrevYears_Grade_Min', 'PrevYears_Grade_Max']].head(5)
    print(sample_df.to_string())
    
    print(f"\nStatistics:")
    print(f"   Mean GPA range: {df['PrevYears_Grade_Mean'].min():.2f} - {df['PrevYears_Grade_Mean'].max():.2f}")
    print(f"   Average Mean GPA: {df['PrevYears_Grade_Mean'].mean():.2f}")
    print(f"   Missing values: {df['PrevYears_Grade_Mean'].isnull().sum()}")
else:
    print("   ⚠ Grades_Prev_Years column not found")

print(f"\nFinal shape: {df.shape}")
print(f"Total columns: {len(df.columns)}")

print(f"\nSaving enhanced dataset to {OUTPUT_FILE}...")
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

print("\n" + "="*80)
print(" FEATURE ENGINEERING COMPLETED")
print("="*80)
print(f"✓ Added 3 numeric grade features")
print(f"✓ Original letter grades preserved in Grades_Prev_Years")
print(f"✓ Dataset ready for machine learning!")
print("="*80)
