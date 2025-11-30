"""
Digital Twin Student Dashboard - Streamlit App
Interactive dashboard for viewing student profiles, roadmaps, and recommendations
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json

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

# Helper functions to load data
@st.cache_data
def load_roadmap(student_id):
    """Load roadmap from local JSON file"""
    roadmap_path = Path(f"roadmaps/{student_id}_roadmap.json")
    if roadmap_path.exists():
        with open(roadmap_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

@st.cache_data
def load_all_recommendations():
    """Load all recommendations from local JSON file"""
    recs_path = Path("recommendations/recommendations.json")
    if recs_path.exists():
        with open(recs_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_student_recommendations(student_id, all_recs):
    """Get recommendations for a specific student"""
    for rec in all_recs:
        if rec.get('student_id') == student_id:
            return rec
    return None

# Title
st.markdown('<div class="main-header">🎓 Digital Twin Student Dashboard</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Student Selection")
    student_id = st.text_input("Enter Student ID", value="S0001", help="Format: S0001 to S1500")
    
    if st.button("🔍 Load Student Data", use_container_width=True):
        st.session_state['load_student'] = student_id
    
    st.divider()
    st.markdown("### Quick Actions")
    export_format = st.selectbox("Export Format", ["JSON", "PDF"])
    
    st.divider()
    st.info("💡 **Standalone Mode**: Loading data from local files")

# Main content
if 'load_student' in st.session_state:
    student_id = st.session_state['load_student']
    
    try:
        # Load data from local files
        with st.spinner("Loading student data..."):
            roadmap = load_roadmap(student_id)
            all_recs = load_all_recommendations()
            recs = get_student_recommendations(student_id, all_recs)
        
        if not roadmap:
            st.error(f"❌ No roadmap found for {student_id}. Please check the student ID.")
            st.stop()
        
        # Header section
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Student ID", student_id)
        with col2:
            if recs:
                st.metric("Target Career", recs.get('target_job', 'N/A'))
        with col3:
            st.metric("Roadmap Stages", len(roadmap.get('stages', [])))
        
        st.divider()
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Roadmap", 
            "📊 Skills Analysis", 
            "🎯 Recommendations", 
            "📈 Career Insights"
        ])
        
        # Tab 1: Roadmap
        with tab1:
            st.subheader("📋 Learning Roadmap")
            
            if recs:
                st.markdown(f"**Student:** {recs.get('student_name', 'Unknown')}")
                st.markdown(f"**Career Path:** {roadmap.get('career_path', 'N/A')}")
                st.markdown(f"**Generated:** {roadmap.get('generated_at', 'N/A')}")
            
            st.divider()
            
            # Display stages
            for stage in roadmap.get('stages', []):
                with st.expander(f"🎯 {stage['stage']} - {stage['duration']}", expanded=True):
                    st.markdown(f"**Focus:** {stage['focus']}")
                    
                    # Skills
                    st.markdown("**Skills to Learn:**")
                    for skill in stage.get('skills', [])[:5]:  # Show top 5
                        st.markdown(f"- {skill}")
                    
                    # Courses
                    if stage.get('courses'):
                        st.markdown("**Recommended Courses:**")
                        for course in stage['courses'][:3]:  # Show top 3
                            st.markdown(f"- **{course['course_name']}** ({course['provider']}) - {course['level']}")
                    
                    # Projects
                    if stage.get('projects'):
                        st.markdown("**Projects:**")
                        for project in stage['projects'][:2]:  # Show top 2
                            st.markdown(f"- **{project['title']}** ({project['difficulty']})")
        
        # Tab 2: Skills Analysis
        with tab2:
            st.subheader("📊 Skills Analysis")
            
            if recs and recs.get('recommended_skills'):
                st.markdown("### Top Priority Skills")
                
                skills_data = []
                for skill_item in recs['recommended_skills'][:10]:
                    skills_data.append({
                        'Skills': skill_item['skill'],
                        'Priority': skill_item['priority']
                    })
                
                df_skills = pd.DataFrame(skills_data)
                st.dataframe(df_skills, use_container_width=True)
                
                # Skills bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=[f"Skill {i+1}" for i in range(len(skills_data))],
                        y=[s['Priority'] for s in skills_data],
                        marker_color='#1f77b4'
                    )
                ])
                fig.update_layout(
                    title="Top Priority Skills",
                    xaxis_title="Skills",
                    yaxis_title="Priority Level",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No skills analysis available for this student.")
        
        # Tab 3: Recommendations
        with tab3:
            st.subheader("🎯 Recommendations")
            
            if recs:
                # Courses
                st.markdown("### 📚 Recommended Courses")
                if recs.get('recommended_courses'):
                    for i, course in enumerate(recs['recommended_courses'][:5], 1):
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.markdown(f"**{i}. {course['course_name']}**")
                            with col2:
                                st.markdown(f"*{course['provider']}*")
                            with col3:
                                st.markdown(f"`{course['level']}`")
                            st.markdown(f"Match Score: {course['score']:.2%}")
                            st.divider()
                
                # Projects
                st.markdown("### 🛠️ Recommended Projects")
                if recs.get('recommended_projects'):
                    for i, project in enumerate(recs['recommended_projects'][:3], 1):
                        with st.expander(f"Project {i}: {project['title'][:80]}..."):
                            st.markdown(f"**Difficulty:** {project['difficulty']}")
                            st.markdown(f"**Description:** {project['description']}")
                            st.markdown(f"**Skills Covered:** {len(project.get('skills_covered', []))} skill sets")
                
                # Internships
                st.markdown("### 💼 Recommended Internships")
                if recs.get('recommended_internships'):
                    for i, internship in enumerate(recs['recommended_internships'][:5], 1):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**{internship['company']}**")
                        with col2:
                            st.markdown(f"{internship['role']}")
                        with col3:
                            st.markdown(f"📍 {internship['location']}")
                        st.progress(internship['match'])
                        st.caption(f"Match: {internship['match']:.1%}")
                        st.divider()
            else:
                st.info("No recommendations available for this student.")
        
        # Tab 4: Career Insights
        with tab4:
            st.subheader("📈 Career Insights")
            
            if recs:
                # Career match comment
                if recs.get('comment'):
                    st.info(f"💡 {recs['comment']}")
                
                # Certification path
                if roadmap.get('certification_path'):
                    st.markdown("### 🎓 Recommended Certifications")
                    for i, cert in enumerate(roadmap['certification_path'], 1):
                        st.markdown(f"{i}. **{cert}**")
                
                # Career distribution pie chart
                if recs.get('recommended_internships'):
                    st.markdown("### 📊 Internship Opportunities by Location")
                    locations = {}
                    for internship in recs['recommended_internships']:
                        loc = internship['location']
                        locations[loc] = locations.get(loc, 0) + 1
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=list(locations.keys()),
                        values=list(locations.values()),
                        hole=.3
                    )])
                    fig.update_layout(title="Internship Distribution by Location")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No career insights available for this student.")
        
    except Exception as e:
        st.error(f"❌ Error loading student data: {str(e)}")
        st.exception(e)

else:
    # Welcome screen
    st.info("👈 Enter a Student ID in the sidebar and click 'Load Student Data' to begin")
    
    st.markdown("""
    ### Welcome to the Digital Twin Student Dashboard
    
    This dashboard provides:
    - 📋 **Personalized Learning Roadmaps** - Stage-by-stage learning paths
    - 📊 **Skills Analysis** - Identify skill gaps and priorities
    - 🎯 **Smart Recommendations** - Courses, projects, and internships
    - 📈 **Career Insights** - Career predictions and certifications
    
    **Available Students:** S0001 to S1500
    """)
