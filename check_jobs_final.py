"""
Final Checks for Jobs Dataset
1. Check for duplicate job_ids
2. Verify date_posted parsing
"""

import pandas as pd
import sys

FILE_PATH = 'egypt_jobs_full_1500_cleaned.csv'
OUTPUT_FILE = 'check_results_safe.txt'

def log(message, file):
    print(message)
    file.write(message + '\n')

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    log(f"Checking {FILE_PATH}...", f)
    try:
        df = pd.read_csv(FILE_PATH)
        
        # 1. Check duplicate job_ids
        if 'job_id' in df.columns:
            duplicates = df['job_id'].duplicated().sum()
            log(f"\n1. Duplicate job_ids: {duplicates}", f)
            if duplicates > 0:
                log("   Duplicate IDs found:", f)
                log(str(df[df['job_id'].duplicated()]['job_id'].head()), f)
            else:
                log("   [OK] All job_ids are unique.", f)
        else:
            log("\n[WARN] job_id column not found!", f)

        # 2. Check date_posted
        if 'date_posted' in df.columns:
            log(f"\n2. date_posted analysis:", f)
            log(f"   Sample values: {df['date_posted'].head(3).tolist()}", f)
            
            # Try parsing
            try:
                df['date_posted_parsed'] = pd.to_datetime(df['date_posted'], errors='coerce')
                valid_dates = df['date_posted_parsed'].notna().sum()
                log(f"   Successfully parsed {valid_dates}/{len(df)} dates.", f)
                if valid_dates < len(df):
                    log("   [WARN] Some dates could not be parsed.", f)
                    log(f"   Invalid samples: {df[df['date_posted_parsed'].isna()]['date_posted'].head().tolist()}", f)
                else:
                    log("   [OK] All dates are parseable.", f)
                    log(f"   Date range: {df['date_posted_parsed'].min()} to {df['date_posted_parsed'].max()}", f)
            except Exception as e:
                log(f"   [ERROR] Error parsing dates: {e}", f)
        else:
            log("\n[WARN] date_posted column not found!", f)
            
    except Exception as e:
        log(f"[ERROR] Failed to process file: {e}", f)
