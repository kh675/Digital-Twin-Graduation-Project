import csv
from datetime import datetime
import sys

FILE_PATH = 'egypt_jobs_full_1500_cleaned.csv'
OUTPUT_FILE = 'check_results_robust.txt'

def log(message, file):
    print(message)
    file.write(message + '\n')

def parse_date(date_str):
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
    log(f"Checking {FILE_PATH} with robust CSV parser...", f_out)
    
    job_ids = set()
    duplicates = []
    valid_dates = 0
    invalid_dates = []
    total_rows = 0
    
    try:
        with open(FILE_PATH, 'r', encoding='utf-8', errors='replace') as f_in:
            # Use csv.reader to handle quoting properly
            reader = csv.DictReader(f_in)
            
            if not reader.fieldnames:
                log("[ERROR] CSV appears empty or malformed (no headers found).", f_out)
                sys.exit(1)
                
            if 'job_id' not in reader.fieldnames:
                log("[ERROR] 'job_id' column missing.", f_out)
            
            if 'date_posted' not in reader.fieldnames:
                log("[ERROR] 'date_posted' column missing.", f_out)

            for i, row in enumerate(reader, start=2): # Start at 2 for line number (1 is header)
                total_rows += 1
                
                # Check job_id
                jid = row.get('job_id', '').strip()
                if jid:
                    if jid in job_ids:
                        duplicates.append((i, jid))
                    else:
                        job_ids.add(jid)
                
                # Check date_posted
                d_str = row.get('date_posted', '').strip()
                if d_str:
                    d_obj = parse_date(d_str)
                    if d_obj:
                        valid_dates += 1
                    else:
                        invalid_dates.append((i, d_str))
                        
    except Exception as e:
        log(f"[CRITICAL ERROR] Failed to read CSV: {e}", f_out)
        sys.exit(1)

    # Report Results
    log(f"\nTotal rows processed: {total_rows}", f_out)
    
    log(f"\n1. Duplicate job_ids: {len(duplicates)}", f_out)
    if duplicates:
        log("   Samples:", f_out)
        for line, jid in duplicates[:5]:
            log(f"   Line {line}: {jid}", f_out)
    else:
        log("   [OK] No duplicates found.", f_out)

    log(f"\n2. Date Parsing:", f_out)
    log(f"   Valid dates: {valid_dates}", f_out)
    log(f"   Invalid dates: {len(invalid_dates)}", f_out)
    if invalid_dates:
        log("   Samples:", f_out)
        for line, d_str in invalid_dates[:5]:
            log(f"   Line {line}: {d_str}", f_out)
    else:
        log("   [OK] All dates parsed successfully.", f_out)
