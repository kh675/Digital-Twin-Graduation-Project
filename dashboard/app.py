"""
Digital Twin Student Dashboard - Streamlit App
Interactive dashboard for viewing student profiles, roadmaps, and recommendations
"""
import streamlit as st
import requests
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

# API configuration
API_BASE = "http://localhost:8000"

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

# Main content
if 'load_student' in st.session_state:
    student_id = st.session_state['load_student']
    
    try:
        # Fetch data from API
        with st.spinner("Loading student data..."):
            roadmap_response = requests.get(f"{API_BASE}/get-roadmap/{student_id}")
            career_response = requests.get(f"{API_BASE}/predict-career/{student_id}")
            recs_response = requests.get(f"{API_BASE}/get-recommendations/{student_id}")
            profile_response = requests.get(f"{API_BASE}/get-profile/{student_id}")
            
            if roadmap_response.status_code != 200:
                st.error(f"Error loading roadmap: {roadmap_response.text}")
                st.stop()
            
            roadmap = roadmap_response.json()
            career = career_response.json() if career_response.status_code == 200 else None
            recs = recs_response.json() if recs_response.status_code == 200 else None
            profile = profile_response.json() if profile_response.status_code == 200 else None
        
        # Header section
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Student ID", student_id)
        with col2:
            if career:
                st.metric("Predicted Career", career['predicted_career'], 
                         f"{career['confidence']*100:.1f}% confidence")
        with col3:
            st.metric("Roadmap Stages", len(roadmap.get('stages', [])))
        
        st.divider()
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📋 Roadmap", 
            "📊 Skills Analysis", 
            "🎯 Recommendations", 
            "📈 Career Insights",
            "🔮 Cluster Insights",
            "👥 Similar Students"
        ])
        
        with tab1:
            st.header("Personalized Learning Roadmap")
            
            # Display certification path
            if 'certification_path' in roadmap:
                st.subheader("🏆 Recommended Certifications")
                cert_cols = st.columns(len(roadmap['certification_path']))
                for idx, cert in enumerate(roadmap['certification_path']):
                    with cert_cols[idx]:
                        st.info(cert)
            
            # Display stages
            for stage in roadmap.get('stages', []):
                with st.expander(f"**{stage['stage']}** — {stage['duration']}", expanded=True):
                    st.markdown(f"**Focus:** {stage.get('focus', 'N/A')}")
                    
                    # Skills
                    if stage.get('skills'):
                        st.markdown("**🎯 Skills to Learn:**")
                        skills_text = ", ".join(stage['skills'][:5]) if len(stage['skills']) > 5 else ", ".join(stage['skills'])
                        st.write(skills_text)
                    
                    # Courses
                    if stage.get('courses'):
                        st.markdown(f"**📚 Courses ({len(stage['courses'])}):**")
                        for course in stage['courses'][:3]:  # Show top 3
                            st.write(f"• {course.get('course_name', 'N/A')} ({course.get('provider', 'N/A')})")
                    
                    # Projects
                    if stage.get('projects'):
                        st.markdown(f"**🛠️ Projects ({len(stage['projects'])}):**")
                        for project in stage['projects']:
                            st.write(f"• {project.get('title', 'N/A')}")
                    
                    # Internships (Advanced stage)
                    if stage.get('internships'):
                        st.markdown(f"**💼 Internship Opportunities ({len(stage['internships'])}):**")
                        for internship in stage['internships']:
                            st.write(f"• {internship.get('role', 'N/A')} at {internship.get('company', 'N/A')} ({internship.get('location', 'N/A')})")
        
        with tab2:
            st.header("Skills Analysis")
            
            if profile and 'skill_gaps' in profile:
                skill_gaps = profile['skill_gaps']
                
                # Missing skills bar chart
                if 'missing_skills' in skill_gaps and skill_gaps['missing_skills']:
                    st.subheader("Top Missing Skills")
                    missing = skill_gaps['missing_skills'][:10]
                    
                    fig = go.Figure(data=[
                        go.Bar(x=list(range(1, len(missing)+1)), y=[1]*len(missing), 
                               text=missing, textposition='auto',
                               marker_color='#ff7f0e')
                    ])
                    fig.update_layout(
                        xaxis_title="Skill Rank",
                        yaxis_title="Priority",
                        showlegend=False,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Skill coverage radar (if available)
                if 'skill_coverage' in skill_gaps:
                    st.subheader("Skill Coverage Analysis")
                    coverage = skill_gaps['skill_coverage']
                    
                    categories = list(coverage.keys())[:8]
                    values = [coverage[cat] for cat in categories]
                    
                    fig = go.Figure(data=go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        marker_color='#1f77b4'
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=False,
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.header("Personalized Recommendations")
            
            if recs:
                # Course recommendations
                if 'recommended_courses' in recs:
                    st.subheader(f"📚 Recommended Courses ({len(recs['recommended_courses'])})")
                    courses_df = pd.DataFrame(recs['recommended_courses'][:10])
                    if not courses_df.empty:
                        st.dataframe(
                            courses_df[['course_name', 'provider', 'level', 'score']],
                            use_container_width=True,
                            hide_index=True
                        )
                
                # Job recommendations
                if 'recommended_jobs' in recs:
                    st.subheader(f"💼 Recommended Jobs ({len(recs['recommended_jobs'])})")
                    jobs_df = pd.DataFrame(recs['recommended_jobs'][:5])
                    if not jobs_df.empty:
                        for _, job in jobs_df.iterrows():
                            with st.container():
                                st.markdown(f"**{job.get('job_title', 'N/A')}**")
                                st.write(f"Match Score: {job.get('match_score', 0):.2%}")
                                st.divider()
        
        with tab4:
            st.header("Career Prediction Insights")
            
            if career and 'probabilities' in career:
                st.subheader("Career Probability Distribution")
                
                probs = career['probabilities']
                careers = list(probs.keys())
                prob_values = list(probs.values())
                
                # Sort by probability
                sorted_data = sorted(zip(careers, prob_values), key=lambda x: x[1], reverse=True)
                careers_sorted, probs_sorted = zip(*sorted_data)
                
                fig = go.Figure(data=[
                    go.Bar(x=list(careers_sorted), y=list(probs_sorted),
                           marker_color=['#2ca02c' if c == career['predicted_career'] else '#1f77b4' 
                                        for c in careers_sorted])
                ])
                fig.update_layout(
                    xaxis_title="Career Path",
                    yaxis_title="Probability",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Timeline visualization
                st.subheader("Learning Timeline")
                stages_data = []
                start_week = 0
                for stage in roadmap.get('stages', []):
                    duration_str = stage.get('duration', '4 weeks')
                    weeks = int(duration_str.split()[0].split('-')[0])  # Extract first number
                    stages_data.append({
                        'Stage': stage['stage'],
                        'Start': start_week,
                        'Duration': weeks
                    })
                    start_week += weeks
                
                if stages_data:
                    fig = go.Figure()
                    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
                    for idx, stage in enumerate(stages_data):
                        fig.add_trace(go.Bar(
                            name=stage['Stage'],
                            x=[stage['Duration']],
                            y=[stage['Stage']],
                            orientation='h',
                            marker_color=colors[idx % len(colors)]
                        ))
                    
                    fig.update_layout(
                        xaxis_title="Weeks",
                        yaxis_title="Stage",
                        barmode='stack',
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab5:
            st.header("🔮 Cluster Insights")
            
            try:
                # Get cluster information for this student
                cluster_response = requests.get(f"{API_BASE}/cluster-student/{student_id}")
                
                if cluster_response.status_code == 200:
                    cluster_data = cluster_response.json()
                    
                    # Display cluster membership
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Cluster", cluster_data['cluster_label'])
                    with col2:
                        st.metric("Cluster Size", cluster_data['cluster_size'])
                    with col3:
                        st.metric("Cluster ID", cluster_data['cluster_id'])
                    
                    st.divider()
                    
                    # Get cluster profile
                    profile_response = requests.get(f"{API_BASE}/cluster-profile/{cluster_data['cluster_label']}")
                    if profile_response.status_code == 200:
                        cluster_profile = profile_response.json()
                        
                        st.subheader(f"📊 {cluster_data['cluster_label']} Cluster Analytics")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Average GPA", f"{cluster_profile['avg_gpa']:.2f}")
                            st.metric("Average Attendance", f"{cluster_profile['avg_attendance']:.1f}%")
                        
                        with col2:
                            st.markdown("**🎯 Top Missing Skills in Cluster:**")
                            for skill in cluster_profile['top_missing_skills'][:5]:
                                st.write(f"• {skill}")
                    
                    st.divider()
                    
                    # Show cluster members
                    st.subheader("👥 Cluster Members (Sample)")
                    members = cluster_data['cluster_members'][:10]
                    member_cols = st.columns(5)
                    for idx, member in enumerate(members):
                        with member_cols[idx % 5]:
                            st.info(member)
                    
                    # Get all clusters overview
                    st.divider()
                    st.subheader("📈 All Clusters Overview")
                    
                    all_clusters_response = requests.get(f"{API_BASE}/all-clusters")
                    if all_clusters_response.status_code == 200:
                        all_clusters = all_clusters_response.json()
                        
                        # Create bar chart of cluster sizes
                        cluster_labels = [c['label'] for c in all_clusters['clusters']]
                        cluster_sizes = [c['member_count'] for c in all_clusters['clusters']]
                        
                        fig = go.Figure(data=[
                            go.Bar(
                                x=cluster_labels,
                                y=cluster_sizes,
                                marker_color=['#2ca02c' if label == cluster_data['cluster_label'] else '#1f77b4' 
                                            for label in cluster_labels],
                                text=cluster_sizes,
                                textposition='auto'
                            )
                        ])
                        fig.update_layout(
                            title="Student Distribution Across Clusters",
                            xaxis_title="Cluster",
                            yaxis_title="Number of Students",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Cluster comparison table
                        st.subheader("📋 Cluster Comparison")
                        cluster_df = pd.DataFrame(all_clusters['clusters'])
                        cluster_df = cluster_df[['label', 'member_count', 'avg_gpa']]
                        cluster_df.columns = ['Cluster', 'Members', 'Avg GPA']
                        st.dataframe(cluster_df, use_container_width=True, hide_index=True)
                
                else:
                    st.warning("⚠️ Cluster data not available. Please run `python clustering_engine.py` first.")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API for cluster data")
            except Exception as e:
                st.warning(f"⚠️ Cluster data not available: {str(e)}")
                st.info("Run `python clustering_engine.py` to generate cluster data")
        
        with tab6:
            st.header("👥 Similar Students")
            
            try:
                # Get similar students
                similar_response = requests.get(f"{API_BASE}/similar-students/{student_id}")
                
                if similar_response.status_code == 200:
                    similar_data = similar_response.json()
                    
                    st.subheader(f"🔍 Students Similar to {student_id}")
                    st.write("Based on skills, academic performance, and career trajectory")
                    
                    st.divider()
                    
                    # Display similar students
                    similar_students = similar_data['similar_students']
                    
                    for idx, similar_student in enumerate(similar_students, 1):
                        with st.expander(f"#{idx}: {similar_student['student_id']} - {similar_student['career_path']}", expanded=(idx <= 3)):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Student ID:** {similar_student['student_id']}")
                                st.write(f"**Career Path:** {similar_student['career_path']}")
                            
                            with col2:
                                # Try to get additional info
                                try:
                                    sim_career = requests.get(f"{API_BASE}/predict-career/{similar_student['student_id']}")
                                    if sim_career.status_code == 200:
                                        sim_career_data = sim_career.json()
                                        st.write(f"**Confidence:** {sim_career_data['confidence']*100:.1f}%")
                                except:
                                    pass
                            
                            # Add action buttons
                            if st.button(f"View {similar_student['student_id']}'s Roadmap", key=f"view_{similar_student['student_id']}"):
                                st.session_state['load_student'] = similar_student['student_id']
                                st.rerun()
                    
                    # Similarity network visualization (optional)
                    st.divider()
                    st.subheader("📊 Similarity Network")
                    st.info("💡 These students share similar skill profiles and career goals. Consider forming study groups or collaborating on projects!")
                    
                else:
                    st.warning("⚠️ Similar students data not available. Please run `python clustering_engine.py` first.")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API for similarity data")
            except Exception as e:
                st.warning(f"⚠️ Similarity data not available: {str(e)}")
                st.info("Run `python clustering_engine.py` to generate similarity data")
        
        # Export section
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export as JSON", use_container_width=True):
                json_str = json.dumps(roadmap, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"{student_id}_roadmap.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📄 Export as PDF", use_container_width=True):
                st.info("PDF export feature coming soon! Use JSON export for now.")
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Please ensure the API server is running on http://localhost:8000")
        st.info("Run: `uvicorn api.main:app --reload --port 8000`")
    except Exception as e:
        st.error(f"❌ Error loading student data: {str(e)}")
        st.exception(e)

else:
    # Welcome screen
    st.info("👈 Enter a Student ID in the sidebar and click 'Load Student Data' to begin")
    
    st.markdown("""
    ### Features:
    - 📋 **Personalized Roadmaps**: View 3-stage learning paths
    - 📊 **Skills Analysis**: Identify skill gaps and coverage
    - 🎯 **Smart Recommendations**: Courses, jobs, and internships
    - 📈 **Career Insights**: ML-powered career predictions
    - 📥 **Export Options**: Download roadmaps as JSON or PDF
    
    ### Quick Start:
    1. Enter a Student ID (S0001 to S1500)
    2. Click "Load Student Data"
    3. Explore the tabs for different insights
    """)
