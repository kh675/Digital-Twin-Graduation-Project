"""
Personality-Based Career Classifier Pipeline
Suggests best career track based on personality traits and preferences
"""

def classify_personality(form_data) -> str:
    """
    Classify student's personality and suggest best career track
    
    Args:
        form_data: StudentForm object with personality fields
        
    Returns:
        Recommended career track based on personality
    """
    score = 0
    
    # Logic-oriented students
    if form_data.enjoy_logic:
        score += 2
    
    # Creative students
    if form_data.enjoy_creativity:
        score += 2
    
    # Team players
    if form_data.teamwork_or_solo == "teamwork":
        score += 1
    
    # Introverts may prefer backend/data work
    if form_data.introvert_or_extrovert == "introvert":
        score -= 1
    
    # Classify based on score
    if score >= 3:
        return "AI / Data Science / Machine Learning"
    elif score >= 1:
        return "Backend Development / Cloud Engineering"
    else:
        return "Frontend Development / UI/UX Design"
