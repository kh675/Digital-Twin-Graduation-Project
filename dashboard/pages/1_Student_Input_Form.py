import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="Create Digital Twin", page_icon="🧬", layout="wide")

# API Configuration
API_BASE_URL = "http://localhost:8000"  # Update this for production

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        # Personal
        "full_name": "",
        "email": "",
        "phone": "",
        "department": "Computer Science",
        "academic_level": "Freshman",
        "gpa": 0.0,
        
        # Academic
        "completed_courses": [],
        "completed_grades": [],
        "current_courses": [],
        "core_subjects_taken": [],
        "core_subjects_missing": [],
        "electives_taken": [],
        "academic_weaknesses": "",
        
        # Skills
        "technical_skills": [],
        "technical_skill_levels": [],
        "soft_skills": [],
        "languages": [],
        "certifications": [],
        
        # Career
        "desired_career_path": "Data Science",
        "preferred_track": "Data Science",
        "desired_job_role": "",
        "target_company": "",
        "preferred_location": "",
        "preferred_country": "",
        "work_type": "Hybrid",
        
        # Experience
        "external_courses": [],
        "internships": [],
        "hackathons": [],
        "clubs": [],
        "volunteer_work": [],
        "projects": [],
        "github_link": "",
        
        # Personality
        "enjoy_tasks": "",
        "hate_tasks": "",
        "introvert_or_extrovert": "introvert",
        "teamwork_or_solo": "teamwork",
        "enjoy_logic": False,
        "enjoy_creativity": False,
        "dream_job": "",
        "favourite_tech": [],
        "industries_loved": [],
        "hobbies": [],
        
        # Learning Style
        "learning_style": "Visual",
        "learning_speed": "Moderate",
        "daily_hours": 2,
        "weekly_days": 5,
        
        # Motivation
        "goal_6_months": "",
        "goal_2_years": "",
        "why_this_career": "",
        "biggest_challenge": "",
        "grad_year": datetime.now().year + 4
    }

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# Header
st.title("🧬 Create Your Digital Twin")
st.markdown("---")

# Progress Bar
progress = (st.session_state.step - 1) / 7
st.progress(progress)

# Step 1: Personal Information
if st.session_state.step == 1:
    st.header("Step 1: Personal Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data["full_name"] = st.text_input("Full Name", st.session_state.form_data["full_name"])
        st.session_state.form_data["email"] = st.text_input("Email Address", st.session_state.form_data["email"])
        st.session_state.form_data["phone"] = st.text_input("Phone Number", st.session_state.form_data["phone"])
    
    with col2:
        st.session_state.form_data["department"] = st.selectbox(
            "Department", 
            ["Computer Science", "Information Systems", "Artificial Intelligence", "Software Engineering"],
            index=["Computer Science", "Information Systems", "Artificial Intelligence", "Software Engineering"].index(st.session_state.form_data["department"]) if st.session_state.form_data["department"] in ["Computer Science", "Information Systems", "Artificial Intelligence", "Software Engineering"] else 0
        )
        st.session_state.form_data["academic_level"] = st.selectbox(
            "Academic Level",
            ["Freshman", "Sophomore", "Junior", "Senior"],
            index=["Freshman", "Sophomore", "Junior", "Senior"].index(st.session_state.form_data["academic_level"])
        )
        st.session_state.form_data["gpa"] = st.number_input("GPA (0.0 - 4.0)", 0.0, 4.0, float(st.session_state.form_data["gpa"]))

    if st.button("Next ➡️"):
        if not st.session_state.form_data["full_name"]:
            st.error("Please enter your name.")
        else:
            next_step()
            st.rerun()

# Step 2: Academic Profile
elif st.session_state.step == 2:
    st.header("Step 2: Academic Profile")
    
    st.info("Enter courses as comma-separated values (e.g., 'Math 101, CS 102')")
    
    completed_str = st.text_area("Completed Courses", ", ".join(st.session_state.form_data["completed_courses"]))
    st.session_state.form_data["completed_courses"] = [x.strip() for x in completed_str.split(",") if x.strip()]
    
    # Simple grade input for now (could be improved)
    # For demo, we'll just mock grades or ask for average
    # st.session_state.form_data["completed_grades"] = ... 
    # Keeping it simple: assume pass/good grades for now or add a specific input if needed.
    # Let's add a dummy grade list matching length of courses for validity if needed, 
    # or just ask user to input grades string.
    grades_str = st.text_input("Grades (comma separated, matching courses)", ", ".join(map(str, st.session_state.form_data["completed_grades"])))
    try:
        st.session_state.form_data["completed_grades"] = [float(x.strip()) for x in grades_str.split(",") if x.strip()]
    except:
        pass # Handle error gracefully
        
    current_str = st.text_input("Current Semester Courses", ", ".join(st.session_state.form_data["current_courses"]))
    st.session_state.form_data["current_courses"] = [x.strip() for x in current_str.split(",") if x.strip()]
    
    core_taken_str = st.text_area("Core Subjects Taken", ", ".join(st.session_state.form_data["core_subjects_taken"]))
    st.session_state.form_data["core_subjects_taken"] = [x.strip() for x in core_taken_str.split(",") if x.strip()]
    
    core_missing_str = st.text_area("Core Subjects Missing", ", ".join(st.session_state.form_data["core_subjects_missing"]))
    st.session_state.form_data["core_subjects_missing"] = [x.strip() for x in core_missing_str.split(",") if x.strip()]
    
    electives_str = st.text_area("Electives Taken", ", ".join(st.session_state.form_data["electives_taken"]))
    st.session_state.form_data["electives_taken"] = [x.strip() for x in electives_str.split(",") if x.strip()]
    
    st.session_state.form_data["academic_weaknesses"] = st.text_area("Academic Weaknesses", st.session_state.form_data["academic_weaknesses"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("Next ➡️"):
            if len(st.session_state.form_data["completed_courses"]) != len(st.session_state.form_data["completed_grades"]):
                st.error("Number of grades must match number of completed courses.")
            else:
                next_step()
                st.rerun()

# Step 3: Skills
elif st.session_state.step == 3:
    st.header("Step 3: Skills & Certifications")
    
    tech_skills_str = st.text_area("Technical Skills (comma separated)", ", ".join(st.session_state.form_data["technical_skills"]))
    st.session_state.form_data["technical_skills"] = [x.strip() for x in tech_skills_str.split(",") if x.strip()]
    
    # Levels - simplified for UI
    # st.session_state.form_data["technical_skill_levels"] 
    
    soft_skills_options = ["Communication", "Teamwork", "Leadership", "Problem Solving", "Time Management", "Critical Thinking"]
    st.session_state.form_data["soft_skills"] = st.multiselect("Soft Skills", soft_skills_options, default=[s for s in st.session_state.form_data["soft_skills"] if s in soft_skills_options])
    
    langs_str = st.text_input("Languages", ", ".join(st.session_state.form_data["languages"]))
    st.session_state.form_data["languages"] = [x.strip() for x in langs_str.split(",") if x.strip()]
    
    certs_str = st.text_area("Certifications", ", ".join(st.session_state.form_data["certifications"]))
    st.session_state.form_data["certifications"] = [x.strip() for x in certs_str.split(",") if x.strip()]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("Next ➡️"):
            next_step()
            st.rerun()

# Step 4: Personality
elif st.session_state.step == 4:
    st.header("Step 4: Personality & Interests")
    
    st.session_state.form_data["enjoy_tasks"] = st.text_area("What tasks do you enjoy?", st.session_state.form_data["enjoy_tasks"])
    st.session_state.form_data["hate_tasks"] = st.text_area("What tasks do you dislike?", st.session_state.form_data["hate_tasks"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.form_data["introvert_or_extrovert"] = st.radio("Are you?", ["introvert", "extrovert"], index=0 if st.session_state.form_data["introvert_or_extrovert"] == "introvert" else 1)
        st.session_state.form_data["teamwork_or_solo"] = st.radio("Preference?", ["teamwork", "solo"], index=0 if st.session_state.form_data["teamwork_or_solo"] == "teamwork" else 1)
    
    with col2:
        st.session_state.form_data["enjoy_logic"] = st.checkbox("I enjoy logic/math problems", st.session_state.form_data["enjoy_logic"])
        st.session_state.form_data["enjoy_creativity"] = st.checkbox("I enjoy creative/design tasks", st.session_state.form_data["enjoy_creativity"])
    
    st.session_state.form_data["dream_job"] = st.text_input("Dream Job", st.session_state.form_data["dream_job"])
    
    favtech_str = st.text_input("Favourite Technologies", ", ".join(st.session_state.form_data["favourite_tech"]))
    st.session_state.form_data["favourite_tech"] = [x.strip() for x in favtech_str.split(",") if x.strip()]

    industries_str = st.text_input("Industries You Love", ", ".join(st.session_state.form_data["industries_loved"]))
    st.session_state.form_data["industries_loved"] = [x.strip() for x in industries_str.split(",") if x.strip()]
    
    hobbies_str = st.text_input("Hobbies", ", ".join(st.session_state.form_data["hobbies"]))
    st.session_state.form_data["hobbies"] = [x.strip() for x in hobbies_str.split(",") if x.strip()]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("Next ➡️"):
            next_step()
            st.rerun()

# Step 5: Career Preferences
elif st.session_state.step == 5:
    st.header("Step 5: Career Preferences")
    
    career_options = ["Data Science", "Web Development", "Cybersecurity", "AI Engineer", "Software Engineering", "Cloud Computing"]
    st.session_state.form_data["desired_career_path"] = st.selectbox("Desired Career Path", career_options, index=career_options.index(st.session_state.form_data["desired_career_path"]) if st.session_state.form_data["desired_career_path"] in career_options else 0)
    
    st.session_state.form_data["preferred_track"] = st.selectbox("Preferred Track", career_options, index=career_options.index(st.session_state.form_data["preferred_track"]) if st.session_state.form_data["preferred_track"] in career_options else 0)
    
    st.session_state.form_data["desired_job_role"] = st.text_input("Desired Job Role", st.session_state.form_data["desired_job_role"])
    st.session_state.form_data["target_company"] = st.text_input("Target Company", st.session_state.form_data["target_company"])
    
    st.session_state.form_data["preferred_country"] = st.text_input("Preferred Country", st.session_state.form_data["preferred_country"])
    
    st.session_state.form_data["work_type"] = st.selectbox("Preferred Work Type", ["Remote", "Hybrid", "Onsite"], index=["Remote", "Hybrid", "Onsite"].index(st.session_state.form_data["work_type"]))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("Next ➡️"):
            next_step()
            st.rerun()

# Step 6: Experience
elif st.session_state.step == 6:
    st.header("Step 6: Experience & Activities")
    
    ext_courses_str = st.text_area("External Courses (Udemy, etc.)", ", ".join(st.session_state.form_data["external_courses"]))
    st.session_state.form_data["external_courses"] = [x.strip() for x in ext_courses_str.split(",") if x.strip()]
    
    internships_str = st.text_area("Internships", ", ".join(st.session_state.form_data["internships"]))
    st.session_state.form_data["internships"] = [x.strip() for x in internships_str.split(",") if x.strip()]
    
    projects_str = st.text_area("Personal Projects", ", ".join(st.session_state.form_data["projects"]))
    st.session_state.form_data["projects"] = [x.strip() for x in projects_str.split(",") if x.strip()]
    
    volunteer_str = st.text_area("Volunteer Work", ", ".join(st.session_state.form_data["volunteer_work"]))
    st.session_state.form_data["volunteer_work"] = [x.strip() for x in volunteer_str.split(",") if x.strip()]
    
    st.session_state.form_data["github_link"] = st.text_input("GitHub/Portfolio Link", st.session_state.form_data["github_link"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("Next ➡️"):
            next_step()
            st.rerun()

# Step 7: Learning Style & Submit
elif st.session_state.step == 7:
    st.header("Step 7: Learning Style & Goals")
    
    col1, col2 = st.columns(2)
    with col1:
        learning_styles = ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Project-based"]
        st.session_state.form_data["learning_style"] = st.selectbox("Learning Style", learning_styles, index=learning_styles.index(st.session_state.form_data["learning_style"]) if st.session_state.form_data["learning_style"] in learning_styles else 0)
        
        learning_speeds = ["Fast", "Moderate", "Slow & Steady"]
        st.session_state.form_data["learning_speed"] = st.selectbox("Learning Speed", learning_speeds, index=learning_speeds.index(st.session_state.form_data["learning_speed"]) if st.session_state.form_data["learning_speed"] in learning_speeds else 1)
    
    with col2:
        st.session_state.form_data["daily_hours"] = st.slider("Daily Study Hours", 1, 12, st.session_state.form_data["daily_hours"])
        st.session_state.form_data["weekly_days"] = st.slider("Weekly Study Days", 1, 7, st.session_state.form_data["weekly_days"])
        
    st.session_state.form_data["goal_6_months"] = st.text_area("Goal for next 6 months", st.session_state.form_data["goal_6_months"])
    st.session_state.form_data["goal_2_years"] = st.text_area("Goal for next 2 years", st.session_state.form_data["goal_2_years"])
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("🚀 CREATE MY DIGITAL TWIN", type="primary", use_container_width=True):
            
            # Prepare Payload
            payload = st.session_state.form_data.copy()
            # Ensure student_id is present (even if dummy, backend overrides)
            payload["student_id"] = "NEW" 
            
            with st.spinner("🧠 Analyzing profile, predicting career, and generating roadmap..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/create_digital_twin", json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.result = result
                        st.session_state.step = 8 # Move to results page
                        st.rerun()
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# Step 8: Results
elif st.session_state.step == 8:
    if 'result' in st.session_state:
        res = st.session_state.result
        dt = res.get("digital_twin", {})
        
        st.success("Digital Twin Created Successfully!")
        
        # Save ID and trigger redirect
        st.session_state["student_id"] = res.get('student_id')
        st.session_state["go_to_results"] = True
        st.switch_page("pages/2_Results.py")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎯 Recommended Career Track")
            st.info(f"**{dt.get('best_track', 'Unknown')}**")
            
            st.subheader("🚀 Top Career Predictions")
            # Mocking probabilities if not in simple response, or extracting if available
            # The current pipeline returns 'best_track'. 
            # If 'top_careers' is added to pipeline output, display it here.
            # For now, we show the best track.
            
            st.subheader("📚 Recommended Courses")
            for course in dt.get("recommended_courses", []):
                st.write(f"- {course}")
                
            st.subheader("🛠️ Missing Skills")
            st.write(", ".join(dt.get("missing_skills", [])))
            
        with col2:
            st.subheader("💼 Recommended Roles")
            for role in dt.get("recommended_job_roles", []):
                st.write(f"- {role}")
                
            st.subheader("🏢 Target Companies")
            for comp in dt.get("recommended_companies", []):
                st.write(f"- {comp}")
                
            # PDF Download
            pdf_url = res.get("pdf_url")
            if pdf_url:
                # In a real deployed scenario, this URL needs to be reachable.
                # For localhost, it might be http://localhost:8000/pdf_reports/...
                # We can try to fetch the content if it's a relative path or construct full URL
                full_pdf_url = f"{API_BASE_URL}{pdf_url}"
                try:
                    pdf_resp = requests.get(full_pdf_url)
                    if pdf_resp.status_code == 200:
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_resp.content,
                            file_name=f"{res.get('student_id')}_report.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.warning("PDF generated but could not be downloaded directly.")
                except:
                     st.warning("Could not connect to download PDF.")

    if st.button("Create Another Profile"):
        st.session_state.step = 1
        st.rerun()
