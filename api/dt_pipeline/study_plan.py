"""
Study Plan Generator Pipeline
Creates weekly study schedule based on roadmap and available time
"""
from typing import List, Dict

def generate_study_plan(roadmap_skills: List[str], daily_hours: int) -> List[Dict]:
    """
    Generate weekly study plan based on roadmap and available study time
    
    Args:
        roadmap_skills: List of skills from personalized roadmap
        daily_hours: Hours per day student can study
        
    Returns:
        List of weekly study plan items with week number, skill, and hours
    """
    study_plan = []
    week = 1
    
    # Distribute skills across weeks based on available time
    for skill in roadmap_skills[:12]:  # First 12 weeks
        study_plan.append({
            "week": week,
            "skill": skill,
            "hours_per_week": daily_hours * 5,  # 5 study days per week
            "focus": "Theory and Practice"
        })
        week += 1
    
    return study_plan
