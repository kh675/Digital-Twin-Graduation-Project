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
    r = requests.get(f"{API_BASE_URL}/get_digital_twin/{sid}")
    if r.status_code == 200:
        return r.json()
    return None

data = get_twin(student_id)

if not data:
    st.error("Could not load Digital Twin for this student.")
    st.stop()

twin = data["digital_twin"]
skills = twin.get("skills", {})
probs = twin.get("career_probabilities", {})

st.success(f"Loaded Digital Twin for: {student_id}")

# -----------------------------
# Skill Radar Chart
# -----------------------------
if skills:
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(skills.values()),
        theta=list(skills.keys()),
        fill='toself'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False
    )
    st.plotly_chart(fig)
else:
    st.info("No skill data available.")

# -----------------------------
# Career Probability Bar Chart
# -----------------------------
if probs:
    df = pd.DataFrame(list(probs.items()), columns=["Career", "Probability"])
    fig = px.bar(df, x="Career", y="Probability")
    st.plotly_chart(fig)
else:
    st.info("No prediction data available.")
