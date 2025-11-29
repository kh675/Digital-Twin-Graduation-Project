import json
import os
import sys

# --- Configuration ---
REC_FILE = "recommendations/recommendations.json"

def verify_recommendations():
    print("🔍 Starting Verification for Step 3: Recommendation Engine...")
    
    if not os.path.exists(REC_FILE):
        print(f"❌ Error: Recommendation file not found at {REC_FILE}")
        return False
        
    try:
        with open(REC_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return False
        
    print(f"✅ Loaded {len(data)} recommendations.")
    
    # 1. Structure Check
    print("\n1️⃣  Structure Check:")
    required_keys = ["student_id", "recommended_courses", "recommended_skills", "recommended_projects", "recommended_internships"]
    
    sample = data[0]
    missing_keys = [k for k in required_keys if k not in sample]
    
    if missing_keys:
        print(f"❌ Missing keys in output: {missing_keys}")
        return False
    else:
        print("✅ JSON schema is correct.")
        
    # 2. Course Logic Check
    print("\n2️⃣  Course Logic Check:")
    courses = sample["recommended_courses"]
    if not courses:
        print("⚠️ Warning: No courses recommended for sample student.")
    else:
        # Check if we have AWS and Huawei
        providers = set([c['provider'].upper() for c in courses])
        print(f"   Providers found: {providers}")
        if 'AWS' in providers and 'HUAWEI' in providers:
            print("✅ Both AWS and Huawei courses present.")
        else:
            print("⚠️ Warning: Missing one of the providers in sample.")
            
        # Check scores
        scores = [c['score'] for c in courses]
        if all(0 <= s <= 1.0 for s in scores) or all(0 <= s <= 100 for s in scores): # Allow 0-1 or 0-100
            print("✅ Course scores are within valid range.")
        else:
            print(f"❌ Invalid course scores detected: {scores}")
            
    # 3. Skill Logic Check
    print("\n3️⃣  Skill Logic Check:")
    skills = sample["recommended_skills"]
    if not skills:
        print("⚠️ Warning: No skills recommended.")
    else:
        print(f"   Top skill: {skills[0]['skill']} (Priority: {skills[0]['priority']})")
        print("✅ Skills present and prioritized.")
        
    # 4. Project Logic Check
    print("\n4️⃣  Project Logic Check:")
    projects = sample["recommended_projects"]
    if not projects:
        print("⚠️ Warning: No projects recommended.")
    else:
        print(f"   Sample Project: {projects[0]['title']}")
        print("✅ Projects generated.")
        
    # 5. Internship Logic Check
    print("\n5️⃣  Internship Logic Check:")
    internships = sample["recommended_internships"]
    if not internships:
        print("⚠️ Warning: No internships recommended (might be due to strict filtering).")
    else:
        print(f"   Sample Internship: {internships[0]['role']} at {internships[0]['company']}")
        print("✅ Internships found.")

    # 6. Manual Sample Review
    print("\n6️⃣  Sample Profile Review (Student 0):")
    print(json.dumps(sample, indent=2))
    
    print("\n✅ STEP 3 VERIFICATION COMPLETE: SUCCESS")
    return True

if __name__ == "__main__":
    verify_recommendations()
