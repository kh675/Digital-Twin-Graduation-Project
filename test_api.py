"""
Test script for Digital Twin API
Run: pytest test_api.py
"""
import requests
import pytest

API_BASE = "http://localhost:8000"

def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert 'model_loaded' in data

def test_predict_career():
    """Test career prediction endpoint"""
    response = requests.get(f"{API_BASE}/predict-career/S0001")
    assert response.status_code == 200
    data = response.json()
    assert 'student_id' in data
    assert 'predicted_career' in data
    assert 'confidence' in data
    assert 'probabilities' in data
    assert data['student_id'] == 'S0001'

def test_get_roadmap():
    """Test roadmap endpoint"""
    response = requests.get(f"{API_BASE}/get-roadmap/S0001")
    assert response.status_code == 200
    data = response.json()
    assert 'student_id' in data
    assert 'career_path' in data
    assert 'stages' in data
    assert len(data['stages']) == 3

def test_get_recommendations():
    """Test recommendations endpoint"""
    response = requests.get(f"{API_BASE}/get-recommendations/S0001")
    assert response.status_code == 200
    data = response.json()
    assert 'student_id' in data
    assert 'recommended_courses' in data

def test_get_profile():
    """Test profile endpoint"""
    response = requests.get(f"{API_BASE}/get-profile/S0001")
    assert response.status_code == 200
    data = response.json()
    assert 'student_id' in data
    assert 'skill_gaps' in data

def test_invalid_student():
    """Test with invalid student ID"""
    response = requests.get(f"{API_BASE}/get-roadmap/S9999")
    assert response.status_code == 404

def test_list_students():
    """Test list students endpoint"""
    response = requests.get(f"{API_BASE}/list-students?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert 'students' in data
    assert 'total' in data
    assert len(data['students']) <= 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
