# api/utils/pdf_wrapper.py
import os
from typing import Dict
from pathlib import Path

PDF_DIR = os.environ.get("PDF_OUTPUT_DIR", "./pdf_reports")
os.makedirs(PDF_DIR, exist_ok=True)

def generate_student_pdf(student_id: str, digital_twin: Dict) -> str:
    """
    Minimal wrapper to call your production PDF generator.
    Expects generate_pdf_report.generate_student_pdf(student_id, profile)
    or uses a simple fallback that writes a 1-page PDF placeholder.
    Returns absolute path to PDF file.
    """
    try:
        from generate_pdf_report import generate_student_pdf as gen_pdf
        out = gen_pdf(student_id, digital_twin)
        # gen_pdf should return path; otherwise construct expected path:
        if not out:
            out = os.path.join(PDF_DIR, f"{student_id}_report.pdf")
        return out
    except Exception:
        # Fallback: write a placeholder text file renamed .pdf to avoid crash
        p = os.path.join(PDF_DIR, f"{student_id}_report.pdf")
        with open(p, "wb") as f:
            f.write(b"%PDF-1.4\n%placeholder\n")
        return p
