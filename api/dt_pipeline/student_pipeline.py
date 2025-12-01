"""
Student Digital Twin Pipeline
Main AI pipeline for generating complete student digital twin profile
Processes student input and generates personalized recommendations
"""
from typing import Dict, List
import numpy as np

def run_student_pipeline(student: Dict) -> Dict:
    """
    Main AI pipeline for generating the student's digital twin.
    
    Args:
        student: Dictionary containing all student form data
        
    Returns:
        Complete digital twin profile with recommendations
    """

    # ========= 1) CLEAN BASIC INPUT =========
    name = student.get("name")
    gpa = student.get("gpa", 0)
    technical_skills = student.get("technical_skills", [])
    soft_skills = student.get("soft_skills", [])
    major_course_grades = student.get("major_course_grades", {})
    past_courses = student.get("past_courses", [])
    desired_career_path = student.get("desired_career_path")
    preferred_track = student.get("preferred_track")
    interests = student.get("interests", [])
    internships = student.get("internships", [])
    external_courses = student.get("external_courses", [])
    volunteer_work = student.get("volunteer_work", [])
    target_company = student.get("target_company")
    desired_job_role = student.get("desired_job_role")

    # ========= 2) IDENTIFY SKILL GAPS =========
    skill_database = {
        "Data Science": ["Python", "Pandas", "Machine Learning", "SQL", "Statistics", "Deep Learning"],
        "Web Development": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
        "Cybersecurity": ["Networking", "Linux", "Python", "PenTesting", "SIEM"],
        "AI Engineer": ["Python", "ML", "Deep Learning", "NLP", "MLOps"]
    }

    if preferred_track in skill_database:
        required_skills = skill_database[preferred_track]
    else:
        required_skills = []

    missing_skills = [skill for skill in required_skills if skill not in technical_skills]

    # ========= 3) RECOMMEND COURSES =========
    course_recommendations = {
        "Python": "Complete Python Bootcamp – Udemy",
        "Machine Learning": "Andrew Ng ML – Coursera",
        "Deep Learning": "DeepLearning.AI",
        "SQL": "DataCamp SQL Track",
        "React": "Meta Front-End Course – Coursera",
        "PenTesting": "TryHackMe Path"
    }

    recommended_courses = [
        course_recommendations[s] for s in missing_skills if s in course_recommendations
    ]

    # ========= 4) SUGGEST BEST CAREER TRACK =========
    track_scores = {
        "Data Science": 0,
        "Web Development": 0,
        "Cybersecurity": 0,
        "AI Engineer": 0
    }

    # Increase score if skills overlap
    for skill in technical_skills:
        for track, skills in skill_database.items():
            if skill in skills:
                track_scores[track] += 1

    best_track = max(track_scores, key=track_scores.get)

    # ========= 5) JOB ROLE SUGGESTIONS =========
    job_roles = {
        "Data Science": ["Data Analyst", "ML Engineer", "Data Scientist"],
        "Web Development": ["Frontend Dev", "Fullstack Dev", "Web Engineer"],
        "Cybersecurity": ["SOC Analyst", "PenTester"],
        "AI Engineer": ["AI Research Assistant", "NLP Engineer"]
    }

    recommended_job_roles = job_roles.get(best_track, [])

    # ========= 6) COMPANIES =========
    companies = {
        "Data Science": ["Google", "IBM", "Dell", "Vodafone", "Orange", "Etisalat"],
        "Web Development": ["Vodafone", "Instabug", "Valeo"],
        "Cybersecurity": ["CyberArmy", "EY", "Deloitte"],
        "AI Engineer": ["Microsoft", "OpenAI", "Huawei"]
    }

    recommended_companies = companies.get(best_track, [])

    # ========= 7) OUTPUT DIGITAL TWIN =========
    # Format skills for dashboard (mock scores for now as we only have binary presence)
    skills_with_scores = {skill: 85 for skill in technical_skills}
    
    # Normalize track scores to probabilities
    total_score = sum(track_scores.values()) if sum(track_scores.values()) > 0 else 1
    career_probabilities = {k: round(v / total_score, 2) for k, v in track_scores.items()}

    digital_twin = {
        "student_name": name,
        "best_track": best_track,
        "missing_skills": missing_skills,
        "recommended_courses": recommended_courses,
        "recommended_job_roles": recommended_job_roles,
        "recommended_companies": recommended_companies,
        "input_summary": student,
        # Added for Dashboard visualization
        "skills": skills_with_scores,
        "career_probabilities": career_probabilities
    }

    return digital_twin
