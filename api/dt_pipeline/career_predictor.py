"""
Career Prediction Pipeline
Predicts top career paths with probability scores
"""
from typing import List, Tuple
import numpy as np

def predict_careers(features: List[float]) -> List[Tuple[str, float]]:
    """
    Predict top 5 career paths with probability scores
    
    Args:
        features: Student feature vector (GPA, skills count, etc.)
        
    Returns:
        List of (career_name, probability) tuples, sorted by probability
    """
    # Placeholder - will be implemented in Step 12
    # This will use the trained ML model from models/career_model.pkl
    
    careers = [
        ("Data Analyst", 0.82),
        ("ML Engineer", 0.65),
        ("Backend Developer", 0.58),
        ("Frontend Developer", 0.45),
        ("DevOps Engineer", 0.40)
    ]
    
    return careers
