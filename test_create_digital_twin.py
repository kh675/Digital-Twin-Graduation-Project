import requests
import json

API_URL = "http://localhost:8000/create_digital_twin"

test_payload = {
    "full_name": "Test Student",
    "student_id": "TEST001",
    "email": "test@example.com",
    "phone": "123-456-7890",
    "department": "Computer Science",
    "academic_level": "Senior",
    "gpa": 3.5,

    "completed_courses": ["Intro to Programming", "Data Structures", "Algorithms"],
    "completed_grades": [3.7, 3.8, 3.6],
    "current_courses": ["Machine Learning", "Web Development"],
    "core_subjects_taken": ["Programming", "Math"],
    "core_subjects_missing": ["Networks", "Security"],
    "electives_taken": ["AI", "Cloud Computing"],
    "academic_weaknesses": "Need more practice with networking",

    "technical_skills": ["Python", "SQL", "JavaScript"],
    "technical_skill_levels": ["Advanced", "Intermediate", "Beginner"],
    "soft_skills": ["Communication", "Teamwork"],
    "languages": ["English", "Arabic"],
    "certifications": ["AWS Cloud Practitioner"],

    "desired_career_path": "Data Science",
    "preferred_track": "Data Science",
    "desired_job_role": "Data Analyst",
    "target_company": "Google",
    "preferred_location": "Cairo",
    "preferred_country": "Egypt",
    "work_type": "Hybrid",

    "external_courses": ["Coursera ML", "Udemy Python"],
    "internships": ["Tech Company Summer 2023"],
    "hackathons": ["Hackathon 2023"],
    "clubs": ["CS Club"],
    "volunteer_work": ["Teaching coding"],
    "projects": ["Portfolio Website", "ML Project"],
    "github_link": "https://github.com/testuser",

    "enjoy_tasks": "I enjoy solving complex problems and building ML models",
    "hate_tasks": "Repetitive manual tasks",
    "introvert_or_extrovert": "introvert",
    "teamwork_or_solo": "teamwork",
    "enjoy_logic": True,
    "enjoy_creativity": False,
    "dream_job": "Lead Data Scientist",
    "favourite_tech": ["Python", "TensorFlow", "AWS"],
    "industries_loved": ["Tech", "Finance"],
    "hobbies": ["Reading", "Coding"],

    "learning_style": "Project-based",
    "learning_speed": "Fast",
    "daily_hours": 3,
    "weekly_days": 5,

    "goal_6_months": "Complete ML certification",
    "goal_2_years": "Become ML Engineer",
    "why_this_career": "Passionate about AI and data",
    "biggest_challenge": "Time management",
    "grad_year": 2025
}

print("Sending request to API...")
response = requests.post(API_URL, json=test_payload)

print("Status:", response.status_code)

if response.status_code == 200:
    print("\nAPI Response:")
    data = response.json()
    print(json.dumps(data, indent=4))
else:
    print("Error Response:")
    print(response.text)
