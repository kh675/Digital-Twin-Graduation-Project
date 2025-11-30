"""
Regenerate sample PDFs with updated QR codes pointing to Streamlit Cloud
"""
import sys
from pathlib import Path

# Import the PDF generator
from generate_pdf_report import generate_student_pdf

print("=" * 70)
print("REGENERATING SAMPLE PDFs WITH UPDATED QR CODES")
print("=" * 70)

# Regenerate PDFs for first 10 students as samples
sample_students = [f"S{str(i).zfill(4)}" for i in range(1, 11)]

print(f"\nRegenerating PDFs for {len(sample_students)} students...")
print("Students:", ", ".join(sample_students))

successful = 0
failed = 0

for student_id in sample_students:
    print(f"\n📄 Generating PDF for {student_id}...", end=" ")
    if generate_student_pdf(student_id):
        print("✅ Success")
        successful += 1
    else:
        print("❌ Failed")
        failed += 1

print("\n" + "=" * 70)
print("REGENERATION COMPLETE")
print("=" * 70)
print(f"\n📊 Summary:")
print(f"   Total: {successful + failed}")
print(f"   Successful: {successful}")
print(f"   Failed: {failed}")
print(f"\n✅ PDFs now have QR codes pointing to:")
print(f"   https://digital-twin-graduation-project-jpvgy8jk9pwpgdd89xi7oq.streamlit.app")
print("\n" + "=" * 70)
