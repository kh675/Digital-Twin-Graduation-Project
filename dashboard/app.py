"""
Digital Twin Student Dashboard - Home Page
Welcome page with navigation
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Digital Twin Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎓 Digital Twin Student Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Career Guidance & Personalized Learning Paths</div>', unsafe_allow_html=True)

# Welcome section
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("dashboard/assets/banner.png", use_container_width=True)

st.markdown("---")

# Features
st.markdown("### 🚀 What You Can Do")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📝 Create Your Digital Twin</h3>
        <p>Fill out the Student Input Form to generate your personalized digital twin profile with:</p>
        <ul>
            <li>AI-powered skill gap analysis</li>
            <li>Personalized course recommendations</li>
            <li>Career path predictions</li>
            <li>Custom learning roadmap</li>
            <li>PDF report generation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 View Your Results</h3>
        <p>After creating your digital twin, access:</p>
        <ul>
            <li>Detailed results page with recommendations</li>
            <li>Interactive analytics dashboard</li>
            <li>Skill proficiency charts</li>
            <li>Career probability analysis</li>
            <li>Downloadable PDF reports</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Getting Started
st.markdown("### 🎯 Getting Started")

st.info("""
**New Student?** 
1. Click on **"Student Input Form"** in the sidebar
2. Fill out your information
3. Submit to generate your digital twin
4. View your personalized results and dashboard

**Returning Student?**
1. Go to **"Results"** or **"Dashboard"** in the sidebar
2. Enter your Student ID (e.g., S1503)
3. View your saved digital twin profile
""")

# Statistics
st.markdown("---")
st.markdown("### 📈 Platform Statistics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Students", "1,500+")
with col2:
    st.metric("Career Paths", "6")
with col3:
    st.metric("Course Database", "500+")
with col4:
    st.metric("Accuracy", "95%")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Powered by AI & Machine Learning | Digital Twin Technology</p>
    <p>© 2025 Digital Twin Student Dashboard</p>
</div>
""", unsafe_allow_html=True)
