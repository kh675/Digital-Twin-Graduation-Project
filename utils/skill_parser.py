"""
Skill parsing and normalization utilities for skill gap analysis.
"""

import re
from typing import List, Set, Dict, Tuple


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill string to standard format.
    
    Args:
        skill: Raw skill string
        
    Returns:
        Normalized skill string (lowercase, trimmed, standardized)
    """
    if not skill or not isinstance(skill, str):
        return ""
    
    # Convert to lowercase and strip whitespace
    skill = skill.lower().strip()
    
    # Remove extra whitespace
    skill = re.sub(r'\s+', ' ', skill)
    
    # Common standardizations
    standardizations = {
        'nodejs': 'node.js',
        'node js': 'node.js',
        'reactjs': 'react',
        'react js': 'react',
        'tensorflow': 'tensorflow',
        'tensor flow': 'tensorflow',
        'pytorch': 'pytorch',
        'py torch': 'pytorch',
        'scikit-learn': 'scikit-learn',
        'sklearn': 'scikit-learn',
        'ci/cd': 'ci/cd',
        'cicd': 'ci/cd',
        'tcp/ip': 'tcp/ip',
        'tcpip': 'tcp/ip',
        'rest api': 'rest apis',
        'restful api': 'rest apis',
        'aws': 'aws',
        'amazon web services': 'aws',
        'gcp': 'gcp',
        'google cloud': 'gcp',
        'azure': 'azure',
        'microsoft azure': 'azure',
    }
    
    # Apply standardizations
    for old, new in standardizations.items():
        if skill == old:
            return new
    
    return skill


def parse_skill_list(skill_string: str, separator: str = ';') -> List[str]:
    """
    Parse a delimited skill string into a list of normalized skills.
    
    Args:
        skill_string: Delimited string of skills
        separator: Delimiter character (default: semicolon)
        
    Returns:
        List of normalized skill strings
    """
    if not skill_string or not isinstance(skill_string, str):
        return []
    
    # Split by separator
    skills = skill_string.split(separator)
    
    # Normalize each skill and filter empty strings
    normalized_skills = []
    for skill in skills:
        normalized = normalize_skill(skill)
        if normalized:
            normalized_skills.append(normalized)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in normalized_skills:
        if skill not in seen:
            seen.add(skill)
            unique_skills.append(skill)
    
    return unique_skills


def merge_skill_sets(*skill_lists: List[str]) -> List[str]:
    """
    Merge multiple skill lists into a single deduplicated list.
    
    Args:
        *skill_lists: Variable number of skill lists
        
    Returns:
        Merged list of unique skills
    """
    all_skills = []
    seen = set()
    
    for skill_list in skill_lists:
        if not skill_list:
            continue
            
        for skill in skill_list:
            normalized = normalize_skill(skill)
            if normalized and normalized not in seen:
                seen.add(normalized)
                all_skills.append(normalized)
    
    return all_skills


def calculate_skill_overlap(skills1: List[str], skills2: List[str]) -> Dict[str, any]:
    """
    Calculate overlap metrics between two skill sets.
    
    Args:
        skills1: First skill list
        skills2: Second skill list
        
    Returns:
        Dictionary with overlap metrics:
        - matching: List of skills in both sets
        - missing_from_1: Skills in set2 but not set1
        - missing_from_2: Skills in set1 but not set2
        - match_count: Number of matching skills
        - total_unique: Total unique skills across both sets
        - overlap_percentage: Percentage of overlap
    """
    set1 = set(normalize_skill(s) for s in skills1 if s)
    set2 = set(normalize_skill(s) for s in skills2 if s)
    
    matching = sorted(list(set1 & set2))
    missing_from_1 = sorted(list(set2 - set1))
    missing_from_2 = sorted(list(set1 - set2))
    
    match_count = len(matching)
    total_unique = len(set1 | set2)
    overlap_percentage = (match_count / total_unique * 100) if total_unique > 0 else 0.0
    
    return {
        'matching': matching,
        'missing_from_1': missing_from_1,
        'missing_from_2': missing_from_2,
        'match_count': match_count,
        'total_unique': total_unique,
        'overlap_percentage': round(overlap_percentage, 2)
    }


def extract_skill_frequency(skill_lists: List[List[str]]) -> Dict[str, int]:
    """
    Calculate frequency of each skill across multiple skill lists.
    
    Args:
        skill_lists: List of skill lists
        
    Returns:
        Dictionary mapping skill to frequency count
    """
    frequency = {}
    
    for skill_list in skill_lists:
        if not skill_list:
            continue
            
        # Use set to count each skill only once per list
        unique_skills = set(normalize_skill(s) for s in skill_list if s)
        
        for skill in unique_skills:
            frequency[skill] = frequency.get(skill, 0) + 1
    
    return frequency


def get_top_skills(frequency_dict: Dict[str, int], top_n: int = 10) -> List[Tuple[str, int]]:
    """
    Get top N most frequent skills.
    
    Args:
        frequency_dict: Dictionary mapping skill to frequency
        top_n: Number of top skills to return
        
    Returns:
        List of (skill, frequency) tuples sorted by frequency
    """
    sorted_skills = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_skills[:top_n]
