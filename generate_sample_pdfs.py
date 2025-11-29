"""
Step 8: PDF Report Generator - Sample Generation
Generates PDF reports for first 10 students as demonstration
"""
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("STEP 8: PDF REPORT GENERATOR (SAMPLE)")
print("=" * 70)

# Configuration
BASE = Path(".")
PDF_DIR = BASE / "pdf_reports"
CHARTS_DIR = BASE / "charts_temp"
PDF_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)

PRIMARY_COLOR = colors.HexColor("#1f77b4")

# Load data
print("\n1️⃣  Loading data...")
df_students = pd.read_csv(BASE / "digital_twin_students_1500_cleaned.csv", low_memory=False)
roadmaps_dir = BASE / "roadmaps"

with open(BASE / "skill_gap_profiles" / "student_profiles.json", "r") as f:
    profiles = json.load(f)
profiles_map = {p['student_id']: p for p in profiles}

print(f"   Loaded data for {len(df_students)} students")

# Chart generation functions
def generate_skills_bar_chart(student_id, missing_skills, output_path):
    try:
        top_skills = missing_skills[:10]
        if not top_skills:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 5))
        y_pos = np.arange(len(top_skills))
        ax.barh(y_pos, [1]*len(top_skills), color='#ff7f0e', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_skills)
        ax.invert_yaxis()
        ax.set_xlabel('Priority', fontsize=10)
        ax.set_title(f'Top Missing Skills for {student_id}', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()
        return str(output_path)
    except:
        return None

def generate_timeline_chart(student_id, roadmap_stages, output_path):
    try:
        if not roadmap_stages:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 4))
        start_week = 0
        colors_list = ['#1f77b4', '#ff7f0e', '#2ca02c']
        
        for idx, stage in enumerate(roadmap_stages):
            duration_str = stage.get('duration', '4 weeks')
            weeks = int(duration_str.split()[0].split('-')[0])
            
            ax.barh(idx, weeks, left=start_week, height=0.5, 
                   color=colors_list[idx % len(colors_list)], alpha=0.7,
                   edgecolor='black', linewidth=1)
            
            ax.text(start_week + weeks/2, idx, stage['stage'], 
                   ha='center', va='center', fontweight='bold', fontsize=10)
            
            start_week += weeks
        
        ax.set_yticks(range(len(roadmap_stages)))
        ax.set_yticklabels([s['stage'] for s in roadmap_stages])
        ax.set_xlabel('Weeks', fontsize=10)
        ax.set_title(f'Learning Roadmap Timeline for {student_id}', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()
        return str(output_path)
    except:
        return None

def generate_student_pdf(student_id):
    """Generate PDF report for a student"""
    try:
        student_row = df_students[df_students['StudentID'] == student_id]
        if student_row.empty:
            return False
        
        student_data = student_row.iloc[0]
        
        roadmap_path = roadmaps_dir / f"{student_id}_roadmap.json"
        if not roadmap_path.exists():
            return False
        
        with open(roadmap_path, "r") as f:
            roadmap = json.load(f)
        
        profile = profiles_map.get(student_id, {})
        skill_gaps = profile.get('skill_gaps', {})
        career = roadmap.get('career_path', 'Unknown')
        
        # Create PDF
        pdf_path = PDF_DIR / f"{student_id}_report.pdf"
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                     fontSize=24, textColor=PRIMARY_COLOR,
                                     spaceAfter=30, alignment=TA_CENTER)
        
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                       fontSize=16, textColor=PRIMARY_COLOR,
                                       spaceAfter=12, spaceBefore=12)
        
        # Title
        story.append(Paragraph("Student Learning Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Student Info
        student_info = [
            ['Student ID:', student_id],
            ['Name:', str(student_data.get('Name', 'N/A'))],
            ['Major:', str(student_data.get('Major', 'N/A'))],
            ['GPA:', f"{student_data.get('GPA', 0):.2f}"],
            ['Report Date:', pd.Timestamp.now().strftime('%Y-%m-%d')]
        ]
        
        info_table = Table(student_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Career Prediction
        story.append(Paragraph("Career Prediction", heading_style))
        story.append(Paragraph(f"<b>Predicted Career Path:</b> {career}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Skills Analysis
        story.append(Paragraph("Skills Analysis", heading_style))
        missing_skills = skill_gaps.get('missing_skills', [])
        
        if missing_skills:
            skills_chart_path = CHARTS_DIR / f"{student_id}_skills_bar.png"
            if generate_skills_bar_chart(student_id, missing_skills, skills_chart_path):
                story.append(Image(str(skills_chart_path), width=6*inch, height=3.5*inch))
        
        story.append(PageBreak())
        
        # Learning Roadmap
        story.append(Paragraph("Personalized Learning Roadmap", heading_style))
        stages = roadmap.get('stages', [])
        
        if stages:
            timeline_path = CHARTS_DIR / f"{student_id}_timeline.png"
            if generate_timeline_chart(student_id, stages, timeline_path):
                story.append(Image(str(timeline_path), width=6.5*inch, height=2.5*inch))
            
            story.append(Spacer(1, 0.2*inch))
            
            for stage in stages:
                story.append(Paragraph(f"<b>{stage['stage']}</b> ({stage.get('duration', 'N/A')})", 
                                      styles['Heading3']))
                story.append(Paragraph(f"Focus: {stage.get('focus', 'N/A')}", styles['Normal']))
                
                courses = stage.get('courses', [])
                if courses:
                    story.append(Paragraph(f"<b>Courses ({len(courses)}):</b>", styles['Normal']))
                    for course in courses[:3]:
                        story.append(Paragraph(f"• {course.get('course_name', 'N/A')}", styles['Normal']))
                
                story.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"   Error for {student_id}: {e}")
        return False

# Generate sample PDFs
print("\n2️⃣  Generating sample PDF reports...")
sample_students = df_students['StudentID'].head(10).tolist()

successful = 0
for student_id in sample_students:
    print(f"   Generating {student_id}...")
    if generate_student_pdf(student_id):
        successful += 1
        print(f"   ✓ {student_id} complete")

print("\n" + "=" * 70)
print("SAMPLE PDF GENERATION COMPLETE")
print("=" * 70)
print(f"\n📊 Summary:")
print(f"   Generated: {successful} PDFs")
print(f"   Output directory: {PDF_DIR}")
print("\n" + "=" * 70)
