"""
Curriculum Gap Detection Pipeline
Identifies missing required courses for student's department
"""
from typing import List

def compute_curriculum_gap(core_missing: List[str], completed: List[str]) -> List[str]:
    """
    Compute curriculum gaps by finding courses student hasn't taken
    
    Args:
        core_missing: List of core courses student is missing
        completed: List of courses student has completed
        
    Returns:
        List of courses student still needs to take
    """
    # Remove any courses from missing list that student has actually completed
    actual_gaps = list(set(core_missing) - set(completed))
    
    return actual_gaps
