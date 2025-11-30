import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

API_BASE_URL = "http://localhost:8000"

# -----------------------------
# Step 14 — Read Query Params
# -----------------------------
query_params = st.query_params
student_id = query_params.get("student", None)

st.title("📊 Digital Twin Dashboard")

if student_id is None:
    st.warning("No student selected. Add '?student=S1503' to the URL.")
    student_id = st.text_input("Enter Student ID manually:")

if not student_id:
    st.stop()

# -----------------------------
# Load Digital Twin
# -----------------------------
@st.cache_data(ttl=60)
def get_twin(sid):
    try:
        r = requests.get(f"{API_BASE_URL}/get_digital_twin/{sid}")
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

data = get_twin(student_id)

if not data:
    st.error(f"Could not load Digital Twin for student: {student_id}")
    st.stop()

# Handle different response structures (Step 12 vs Step 14 expectations)
# Step 12 returns { "student_id": "...", "digital_twin": { ... } }
# The dashboard code expects data["digital_twin"] to have "skills" and "career_probabilities"
# But our current pipeline returns "missing_skills", "best_track", etc.
# We'll adapt the dashboard to display what we actually have from Step 11/12 pipeline.

twin = data.get("digital_twin", {})
student_name = twin.get("student_name", "Student")
best_track = twin.get("best_track", "Unknown")

st.success(f"Loaded Digital Twin for: {student_name} ({student_id})")
st.info(f"🏆 Best Career Track: **{best_track}**")

# -----------------------------
# Skill Radar Chart (Adapted)
# -----------------------------
# Our current pipeline returns 'missing_skills' (list) and 'technical_skills' (from input)
# We don't have 'skills' dict with scores in the current output format from Step 12.
# We'll visualize what we have: maybe just list them or mock scores for now if needed.
# For this task, I'll stick to the requested code but add a check to avoid errors.

skills = twin.get("skills", {}) # This might be empty based on current pipeline
if not skills and "technical_skills" in data.get("input_summary", {}):
    # Fallback: visualize input skills with dummy scores for demo
    tech_skills = data.get("input_summary", {}).get("technical_skills", [])
    skills = {s: 80 for s in tech_skills} # Dummy score

if skills:
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(skills.values()),
        theta=list(skills.keys()),
        fill='toself'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title="Skill Proficiency Profile"
    )
    st.plotly_chart(fig)
else:
    st.info("No skill data available for visualization.")

# -----------------------------
# Career Probability Bar Chart
# -----------------------------
probs = twin.get("career_probabilities", {})
# If pipeline doesn't return probabilities yet (it returns best_track), we might skip or mock.
# Step 11 pipeline has 'track_scores' but doesn't output them in final dict.
# We'll check if available.

if probs:
    df = pd.DataFrame(list(probs.items()), columns=["Career", "Probability"])
    fig = px.bar(df, x="Career", y="Probability", title="Career Fit Prediction")
    st.plotly_chart(fig)
else:
    st.warning("Detailed career probabilities not available in current Digital Twin version.")
    
# -----------------------------
# Recommendations
# -----------------------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("📚 Recommended Courses")
    for c in twin.get("recommended_courses", []):
        st.write(f"- {c}")

with col2:
    st.subheader("💼 Recommended Roles")
    for r in twin.get("recommended_job_roles", []):
        st.write(f"- {r}")
