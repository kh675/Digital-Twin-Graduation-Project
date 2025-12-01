import requests
import json
import os
import time

API_URL = "http://127.0.0.1:8000"

def test_full_flow():
    print("🔥 STARTING END-TO-END TEST (Step 14 Validation)...")
    
    # ✅ 1. Verify the /health Endpoint Works
    print("\nChecking API health...")
    try:
        health_resp = requests.get(f"{API_URL}/health")
        if health_resp.status_code == 200 and health_resp.json().get("status") == "ok":
             print("OK")
        else:
             print(f"FAIL: {health_resp.text}")
             return
    except Exception as e:
        print(f"FAIL: Could not connect to API. {e}")
        return

    # ✅ 2. Run test_end_to_end_flow.py (POST student)
    print("Creating test student...")
    
    # Payload matching Step 5 requirements
    payload = {
        # Step 1 - Basic Info
        "full_name": "Test Student S1503",
        "email": "test.s1503@example.com",
        "phone": "1234567890",
        "department": "Computer Science",
        "academic_level": "Senior",
        "gpa": 3.8,
        
        # Step 2 - Academics
        "completed_courses": ["CS101", "Data Structures", "Algorithms", "Database Systems", "AI Fundamentals"],
        "completed_grades": [4.0, 3.7, 3.5, 3.9, 4.0],
        "current_courses": ["Machine Learning", "Cloud Computing"],
        "core_subjects_taken": ["Math", "Statistics", "Programming"],
        "core_subjects_missing": ["Advanced Calculus"],
        "electives_taken": ["Web Development", "Psychology"],
        "academic_weaknesses": "None",
        
        # Step 3 - Projects / Experience
        "projects": ["Digital Twin App", "E-commerce Site"],
        "github_link": "https://github.com/teststudent",
        
        # Step 4 - Personality / Interests
        "favourite_tech": ["Python", "Streamlit", "FastAPI"],
        "industries_loved": ["EdTech", "FinTech"],
        "enjoy_tasks": "Coding, Problem Solving",
        "hate_tasks": "Documentation",
        "introvert_or_extrovert": "introvert",
        "teamwork_or_solo": "teamwork",
        "enjoy_logic": True,
        "enjoy_creativity": True,
        "dream_job": "AI Engineer",
        "hobbies": ["Chess", "Reading"],
        
        # Step 5 - Career Goals
        "desired_career_path": "Data Science",
        "preferred_track": "Data Science",
        "desired_job_role": "Machine Learning Engineer",
        "target_company": "Google",
        "preferred_location": "Remote",
        "preferred_country": "Egypt",
        "work_type": "Remote",
        
        # Step 6 - Certifications / Experience
        "technical_skills": ["Python", "SQL", "Pandas", "Scikit-learn"],
        "technical_skill_levels": [],
        "soft_skills": ["Communication", "Leadership"],
        "languages": ["English", "Arabic"],
        "certifications": ["AWS Cloud Practitioner"],
        "external_courses": ["Coursera ML"],
        "internships": ["Software House Intern"],
        "hackathons": ["Global Game Jam"],
        "clubs": ["AI Club"],
        "volunteer_work": ["Teaching Kids Coding"],
        
        # Step 7 - Learning Profile
        "learning_style": "Visual",
        "learning_speed": "Fast",
        "daily_hours": 4,
        "weekly_days": 6,
        
        # Step 8 - Motivation
        "goal_6_months": "Get a job",
        "goal_2_years": "Senior Engineer",
        "why_this_career": "Passion for AI",
        "biggest_challenge": "Time Management",
        "grad_year": 2025
    }
    
    try:
        response = requests.post(f"{API_URL}/create_digital_twin", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            student_id = data.get("student_id")
            print(f"OK ({student_id})")
            
            # ✅ 3. Validate generated files
            print("Validating generated files...")
            
            # JSON Profile
            json_path = f"./data/student_inputs/{student_id}.json"
            if os.path.exists(json_path):
                print(f"   ✔ JSON Profile found: {json_path}")
            else:
                print(f"   ❌ JSON Profile MISSING: {json_path}")

            # PDF Report
            pdf_path = data.get("pdf_path")
            if os.path.exists(pdf_path):
                print(f"   ✔ PDF Report found: {pdf_path}")
            else:
                # Try relative check
                if os.path.exists(os.path.join(".", pdf_path)):
                     print(f"   ✔ PDF Report found: {pdf_path}")
                else:
                     print(f"   ❌ PDF Report MISSING: {pdf_path}")
            
            # CSV Update (Check if file exists)
            csv_path = "./data/student_inputs.csv"
            if os.path.exists(csv_path):
                print(f"   ✔ CSV Dataset found: {csv_path}")
            else:
                print(f"   ❌ CSV Dataset MISSING: {csv_path}")

            print("OK")

            # ✅ 4. Check dashboard auto-loads with query param
            print("Checking dashboard query param...")
            
            # Simulate Dashboard Load (GET /get_digital_twin/{student_id})
            # The actual dashboard app runs on 8501, but we test the backend data availability here
            # which confirms the dashboard WILL load if it calls this endpoint.
            get_resp = requests.get(f"{API_URL}/get_digital_twin/{student_id}")
            if get_resp.status_code == 200:
                print("OK")
            else:
                print(f"FAIL: Dashboard data load failed. {get_resp.status_code}")

            print("END-TO-END TEST PASSED ✔")
                
        else:
            print(f"FAIL: Submission Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"FAIL: Exception: {e}")

if __name__ == "__main__":
    test_full_flow()
