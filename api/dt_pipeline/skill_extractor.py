"""
AI Skill Extraction Pipeline
Extracts technical skills from free-text input using NLP and pattern matching
"""
from sentence_transformers import SentenceTransformer
import re
from typing import List

# Load sentence transformer model for semantic matching
model = SentenceTransformer("all-MiniLM-L6-v2")

# Common technical skills patterns
SKILL_PATTERNS = [
    "python", "java", "javascript", "react", "angular", "vue", "node.js", "express",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "ml", "machine learning", "ai", "artificial intelligence", "deep learning",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "cloud", "aws", "azure", "gcp", "docker", "kubernetes", "linux",
    "c++", "c#", "go", "rust", "swift", "kotlin",
    "data", "analytics", "visualization", "tableau", "power bi",
    "git", "github", "ci/cd", "devops", "jenkins", "terraform",
    "rest api", "graphql", "microservices", "flask", "django", "fastapi"
]

def extract_skills(text: str) -> List[str]:
    """
    Extract technical skills from text using pattern matching
    
    Args:
        text: Free-form text containing skill descriptions
        
    Returns:
        List of extracted skill names
    """
    found_skills = []
    text_lower = text.lower()
    
    for skill in SKILL_PATTERNS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill.title())
    
    return list(set(found_skills))  # Remove duplicates
