"""
Digital Twin Results Page
Shows personalized recommendations immediately after form submission
This is the "old dashboard" with ML-enhanced recommendations
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from pathlib import Path
import json

API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Results - Digital Twin",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS (same as old dashboard)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stage-card {
        border-left: 4px solid #1f77b4;
        padding-left: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🎯 Your Digital Twin Results</div>', unsafe_allow_html=True)

# Get student ID from session state or query params
if "student_id" in st.session_state:
    student_id = st.session_state["student_id"]
else:
    student_id = st.query_params.get("student", None)

if not student_id:
    st.warning("No student selected. Please fill the Student Input Form.")
    st.stop()

# Load Digital Twin data from API
@st.cache_data(ttl=60)
def get_digital_twin(sid):
    try:
        r = requests.get(f"{API_BASE_URL}/get_digital_twin/{sid}")
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

with st.spinner("Loading your digital twin..."):
    data = get_digital_twin(student_id)

if not data:
    st.error(f"❌ Could not load digital twin for {student_id}")
    st.stop()

twin = data.get("digital_twin", {})
input_data = data.get("input_summary", {})

# Header metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Student ID", student_id)
with col2:
    st.metric("Target Career", twin.get("best_track", "N/A"))
with col3:
    # Calculate match score based on skills
    total_skills = len(input_data.get("technical_skills", []))
    missing_skills = len(twin.get("missing_skills", []))
    match_score = max(0, (total_skills - missing_skills) / max(total_skills, 1) * 100)
    st.metric("Career Match", f"{match_score:.0f}%")

st.success(f"✅ Digital Twin successfully generated for **{input_data.get('full_name', 'Student')}**")

st.divider()

# Create tabs (same structure as old dashboard)
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Roadmap", 
    "📊 Skills Analysis", 
    "🎯 Recommendations", 
    "📈 Career Insights"
])

# Tab 1: Roadmap
with tab1:
    st.subheader("📋 Learning Roadmap")
    
    st.markdown(f"**Student:** {input_data.get('full_name', 'Unknown')}")
    st.markdown(f"**Career Path:** {twin.get('best_track', 'N/A')}")
    st.markdown(f"**Current Level:** {input_data.get('academic_level', 'N/A')}")
    
    st.divider()
    
    # Display recommended courses as roadmap stages
    courses = twin.get("recommended_courses", [])
    if courses:
        st.markdown("### 🎯 Learning Path")
        for i, course in enumerate(courses, 1):
            with st.expander(f"Stage {i}: {course}", expanded=i==1):
                st.markdown(f"**Course:** {course}")
                st.markdown(f"**Priority:** High" if i <= 3 else "**Priority:** Medium")
                st.markdown("**Duration:** 4-6 weeks")
    else:
        st.info("No roadmap stages available yet.")

# Tab 2: Skills Analysis
with tab2:
    st.subheader("📊 Skills Analysis")
    
    # Current skills
    current_skills = input_data.get("technical_skills", [])
    missing_skills = twin.get("missing_skills", [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Your Current Skills")
        if current_skills:
            for skill in current_skills:
                st.markdown(f"- {skill}")
        else:
            st.info("No skills recorded")
    
    with col2:
        st.markdown("### 🎯 Skills to Learn")
        if missing_skills:
            for skill in missing_skills:
                st.markdown(f"- {skill}")
        else:
            st.success("You have all required skills!")
    
    # Skills bar chart
    if current_skills or missing_skills:
        st.markdown("### 📊 Skill Gap Visualization")
        fig = go.Figure(data=[
            go.Bar(name='Current Skills', x=['Skills'], y=[len(current_skills)], marker_color='#2ecc71'),
            go.Bar(name='Missing Skills', x=['Skills'], y=[len(missing_skills)], marker_color='#e74c3c')
        ])
        fig.update_layout(
            title="Skill Gap Analysis",
            yaxis_title="Number of Skills",
            height=400,
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 3: Recommendations
with tab3:
    st.subheader("🎯 Recommendations")
    
    # Courses
    st.markdown("### 📚 Recommended Courses")
    courses = twin.get("recommended_courses", [])
    if courses:
        for i, course in enumerate(courses, 1):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{i}. {course}**")
                with col2:
                    st.markdown(f"`Priority {i}`")
                st.divider()
    else:
        st.info("No course recommendations available")
    
    # Job Roles
    st.markdown("### 💼 Recommended Job Roles")
    roles = twin.get("recommended_job_roles", [])
    if roles:
        for i, role in enumerate(roles, 1):
            st.markdown(f"{i}. **{role}**")
    else:
        st.info("No job role recommendations available")
    
    # Companies
    st.markdown("### 🏢 Target Companies")
    companies = twin.get("recommended_companies", [])
    if companies:
        cols = st.columns(min(len(companies), 3))
        for i, company in enumerate(companies):
            with cols[i % 3]:
                st.markdown(f"**{company}**")
    else:
        st.info("No company recommendations available")

# Tab 4: Career Insights
with tab4:
    st.subheader("📈 Career Insights")
    
    # Career probabilities
    probs = twin.get("career_probabilities", {})
    if probs:
        st.markdown("### 📊 Career Path Fit Analysis")
        df = pd.DataFrame(list(probs.items()), columns=["Career", "Probability"])
        df = df.sort_values("Probability", ascending=False)
        
        fig = px.bar(df, x="Career", y="Probability", 
                     title="Career Fit Scores",
                     color="Probability",
                     color_continuous_scale="Blues")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top career
        top_career = df.iloc[0]
        st.success(f"🎯 **Best Fit:** {top_career['Career']} ({top_career['Probability']:.0%} match)")
    
    # Career advice
    st.markdown("### 💡 Personalized Advice")
    st.info(f"""
    Based on your profile:
    - **Strengths:** {', '.join(current_skills[:3])} 
    - **Focus Areas:** {', '.join(missing_skills[:3]) if missing_skills else 'Continue building expertise'}
    - **Next Steps:** Complete the recommended courses to bridge skill gaps
    - **Timeline:** 6-12 months to reach career readiness
    """)

# Download PDF button
st.divider()
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    pdf_path = f"./pdf_reports/{student_id}_report.pdf"
    try:
        pdf_resp = requests.get(f"{API_BASE_URL}/pdf_reports/{student_id}_report.pdf")
        if pdf_resp.status_code == 200:
            st.download_button(
                label="📄 Download Full PDF Report",
                data=pdf_resp.content,
                file_name=f"{student_id}_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    except:
        st.warning("PDF report not available for download")
