from pydantic import BaseModel
from typing import List, Optional

class StudentForm(BaseModel):
    # Personal Information
    full_name: str
    student_id: str
    email: str
    phone: Optional[str]
    department: str
    academic_level: str
    gpa: float

    # Academic Profile
    completed_courses: List[str]
    completed_grades: List[float]
    current_courses: List[str]
    core_subjects_taken: List[str]
    core_subjects_missing: List[str]
    electives_taken: List[str]
    academic_weaknesses: Optional[str]

    # Skills
    technical_skills: List[str]
    technical_skill_levels: List[str]
    soft_skills: List[str]
    languages: List[str]
    certifications: List[str]

    # Career Preferences
    desired_career_path: str
    preferred_track: str
    desired_job_role: str
    target_company: Optional[str]
    preferred_location: Optional[str]
    preferred_country: Optional[str]
    work_type: str

    # Experiences
    external_courses: List[str]
    internships: List[str]
    hackathons: List[str]
    clubs: List[str]
    volunteer_work: List[str]
    projects: List[str]
    github_link: Optional[str]

    # Personality & Interests
    enjoy_tasks: str
    hate_tasks: str
    introvert_or_extrovert: str
    teamwork_or_solo: str
    enjoy_logic: bool
    enjoy_creativity: bool
    dream_job: str
    favourite_tech: List[str]
    industries_loved: List[str]
    hobbies: List[str]

    # Learning style
    learning_style: str
    learning_speed: str
    daily_hours: int
    weekly_days: int

    # Motivation
    goal_6_months: str
    goal_2_years: str
    why_this_career: str
    biggest_challenge: str
    grad_year: int
