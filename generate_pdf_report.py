"""
Step 8: PDF Report Generator - Production Script
Generates professional PDF reports for all 1500 students with charts and visualizations
"""
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import warnings
warnings.filterwarnings('ignore')

# Try to import QR code library
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("⚠ QR code library not available (install with: pip install qrcode[pil])")

print("=" * 70)
print("STEP 8: PDF REPORT GENERATOR")
print("=" * 70)

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE = Path(".")
PDF_DIR = BASE / "pdf_reports"
CHARTS_DIR = BASE / "charts_temp"
PDF_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)

# Branding colors
PRIMARY_COLOR = colors.HexColor("#1f77b4")
SECONDARY_COLOR = colors.HexColor("#ff7f0e")
SUCCESS_COLOR = colors.HexColor("#2ca02c")

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n1️⃣  Loading data...")

# Load student data
df_students = pd.read_csv(BASE / "digital_twin_students_1500_cleaned.csv", low_memory=False)

# Load roadmaps
roadmaps_dir = BASE / "roadmaps"

# Load skill gap profiles
with open(BASE / "skill_gap_profiles" / "student_profiles.json", "r") as f:
    profiles = json.load(f)
profiles_map = {p['student_id']: p for p in profiles}

# Load career predictions
try:
    df_features = pd.read_csv(BASE / "models" / "features_all.csv")
    career_map = {row['StudentID']: row.get('predicted_career', 'Unknown') 
                  for _, row in df_features.iterrows()}
except:
    career_map = {}

print(f"   Loaded data for {len(df_students)} students")

# ============================================================================
# 2. CHART GENERATION FUNCTIONS
# ============================================================================

def generate_skills_bar_chart(student_id, missing_skills, output_path):
    """Generate bar chart of top missing skills"""
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
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return str(output_path)
    except Exception as e:
        print(f"   Error generating skills chart for {student_id}: {e}")
        return None

def generate_radar_chart(student_id, skill_coverage, output_path):
    """Generate radar chart for skill coverage"""
    try:
        if not skill_coverage or len(skill_coverage) < 3:
            return None
        
        categories = list(skill_coverage.keys())[:8]
        values = [skill_coverage[cat] for cat in categories]
        
        # Close the plot
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values, 'o-', linewidth=2, color='#1f77b4')
        ax.fill(angles, values, alpha=0.25, color='#1f77b4')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=9)
        ax.set_ylim(0, 1)
        ax.set_title(f'Skill Coverage for {student_id}', fontsize=12, fontweight='bold', pad=20)
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return str(output_path)
    except Exception as e:
        print(f"   Error generating radar chart for {student_id}: {e}")
        return None

def generate_timeline_chart(student_id, roadmap_stages, output_path):
    """Generate timeline/Gantt chart for roadmap"""
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
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return str(output_path)
    except Exception as e:
        print(f"   Error generating timeline for {student_id}: {e}")
        return None

def generate_confidence_gauge(student_id, confidence, output_path):
    """Generate confidence gauge chart"""
    try:
        fig, ax = plt.subplots(figsize=(6, 3))
        
        # Create gauge
        ax.barh(0, confidence, height=0.3, color='#2ca02c', alpha=0.7)
        ax.barh(0, 1-confidence, left=confidence, height=0.3, color='#d3d3d3', alpha=0.3)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
        ax.set_yticks([])
        ax.set_title(f'Career Prediction Confidence: {confidence*100:.1f}%', 
                    fontsize=12, fontweight='bold')
        ax.text(confidence/2, 0, f'{confidence*100:.1f}%', 
               ha='center', va='center', fontweight='bold', fontsize=14, color='white')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return str(output_path)
    except Exception as e:
        print(f"   Error generating gauge for {student_id}: {e}")
        return None

def generate_qr_code(student_id, output_path):
    """Generate QR code linking to dashboard"""
    if not QR_AVAILABLE:
        return None
    
    try:
        # Create QR code with dashboard link
        dashboard_url = f"http://localhost:8501/?student={student_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(dashboard_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        return str(output_path)
    except Exception as e:
        print(f"   Error generating QR code for {student_id}: {e}")
        return None

# ============================================================================
# 3. PDF GENERATION FUNCTION
# ============================================================================

def generate_student_pdf(student_id):
    """Generate comprehensive PDF report for a student"""
    try:
        # Load student data
        student_row = df_students[df_students['StudentID'] == student_id]
        if student_row.empty:
            print(f"   ⚠ Student {student_id} not found in database")
            return False
        
        student_data = student_row.iloc[0]
        
        # Load roadmap
        roadmap_path = roadmaps_dir / f"{student_id}_roadmap.json"
        if not roadmap_path.exists():
            print(f"   ⚠ Roadmap not found for {student_id}")
            return False
        
        with open(roadmap_path, "r") as f:
            roadmap = json.load(f)
        
        # Load profile
        profile = profiles_map.get(student_id, {})
        skill_gaps = profile.get('skill_gaps', {})
        
        # Get career prediction
        career = roadmap.get('career_path', 'Unknown')
        confidence = 0.75  # Default confidence
        
        # Create PDF
        pdf_path = PDF_DIR / f"{student_id}_report.pdf"
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=PRIMARY_COLOR,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=PRIMARY_COLOR,
            spaceAfter=12,
            spaceBefore=12
        )
        
        # ====== PAGE 1: HEADER & CAREER PREDICTION ======
        
        # Title
        story.append(Paragraph("Student Learning Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Student Info Table
        student_info = [
            ['Student ID:', student_id],
            ['Name:', student_data.get('Name', 'N/A')],
            ['Major:', student_data.get('Major', 'N/A')],
            ['GPA:', f"{student_data.get('GPA', 0):.2f}"],
            ['Report Date:', pd.Timestamp.now().strftime('%Y-%m-%d')]
        ]
        
        info_table = Table(student_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Career Prediction Section
        story.append(Paragraph("Career Prediction", heading_style))
        story.append(Paragraph(f"<b>Predicted Career Path:</b> {career}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # Generate and add confidence gauge
        gauge_path = CHARTS_DIR / f"{student_id}_gauge.png"
        if generate_confidence_gauge(student_id, confidence, gauge_path):
            story.append(Image(str(gauge_path), width=5*inch, height=2.5*inch))
        
        story.append(PageBreak())
        
        # ====== PAGE 2: SKILLS ANALYSIS ======
        
        story.append(Paragraph("Skills Analysis", heading_style))
        
        missing_skills = skill_gaps.get('missing_skills', [])
        if missing_skills:
            story.append(Paragraph(f"<b>Top Missing Skills ({len(missing_skills[:10])}):</b>", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # Generate skills bar chart
            skills_chart_path = CHARTS_DIR / f"{student_id}_skills_bar.png"
            if generate_skills_bar_chart(student_id, missing_skills, skills_chart_path):
                story.append(Image(str(skills_chart_path), width=6*inch, height=3.5*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Skill coverage radar
        skill_coverage = skill_gaps.get('skill_coverage', {})
        if skill_coverage:
            radar_path = CHARTS_DIR / f"{student_id}_radar.png"
            if generate_radar_chart(student_id, skill_coverage, radar_path):
                story.append(Image(str(radar_path), width=5*inch, height=5*inch))
        
        story.append(PageBreak())
        
        # ====== PAGE 3: LEARNING ROADMAP ======
        
        story.append(Paragraph("Personalized Learning Roadmap", heading_style))
        
        stages = roadmap.get('stages', [])
        if stages:
            # Timeline chart
            timeline_path = CHARTS_DIR / f"{student_id}_timeline.png"
            if generate_timeline_chart(student_id, stages, timeline_path):
                story.append(Image(str(timeline_path), width=6.5*inch, height=2.5*inch))
            
            story.append(Spacer(1, 0.2*inch))
            
            # Stages details
            for stage in stages:
                story.append(Paragraph(f"<b>{stage['stage']}</b> ({stage.get('duration', 'N/A')})", 
                                      styles['Heading3']))
                story.append(Paragraph(f"Focus: {stage.get('focus', 'N/A')}", styles['Normal']))
                
                # Courses
                courses = stage.get('courses', [])
                if courses:
                    story.append(Paragraph(f"<b>Courses ({len(courses)}):</b>", styles['Normal']))
                    for course in courses[:3]:
                        story.append(Paragraph(f"• {course.get('course_name', 'N/A')}", 
                                             styles['Normal']))
                
                story.append(Spacer(1, 0.15*inch))
        
        story.append(PageBreak())
        
        # ====== PAGE 4: CERTIFICATIONS & NEXT STEPS ======
        
        story.append(Paragraph("Recommended Certifications", heading_style))
        
        cert_path = roadmap.get('certification_path', [])
        if cert_path:
            for cert in cert_path:
                story.append(Paragraph(f"• {cert}", styles['Normal']))
        else:
            story.append(Paragraph("No specific certifications recommended", styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # QR Code (if available)
        if QR_AVAILABLE:
            story.append(Paragraph("Access Your Dashboard", heading_style))
            qr_path = CHARTS_DIR / f"{student_id}_qr.png"
            if generate_qr_code(student_id, qr_path):
                story.append(Paragraph("Scan to view your interactive dashboard:", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                story.append(Image(str(qr_path), width=1.5*inch, height=1.5*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], 
                                      fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        story.append(Paragraph(f"Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", 
                             footer_style))
        story.append(Paragraph("Digital Twin Student Success Platform", footer_style))
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"   ❌ Error generating PDF for {student_id}: {e}")
        return False

# ============================================================================
# 4. BATCH GENERATION
# ============================================================================

def generate_all_reports():
    """Generate PDF reports for all students"""
    print("\n2️⃣  Generating PDF reports...")
    
    student_ids = df_students['StudentID'].tolist()
    successful = 0
    failed = 0
    
    from tqdm import tqdm
    for student_id in tqdm(student_ids, desc="Generating PDFs"):
        if generate_student_pdf(student_id):
            successful += 1
        else:
            failed += 1
    
    print(f"\n✅ Successfully generated {successful} PDF reports")
    if failed > 0:
        print(f"⚠ Failed to generate {failed} reports")
    
    return successful, failed

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Starting PDF generation...")
    print("=" * 70)
    
    successful, failed = generate_all_reports()
    
    print("\n" + "=" * 70)
    print("PDF GENERATION COMPLETE")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   Total PDFs: {successful + failed}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Output directory: {PDF_DIR}")
    print("\n" + "=" * 70)
