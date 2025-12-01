import os
import traceback
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import StudentForm model
from api.models.student_form_model import StudentForm

# Import pipeline and utilities
from api.dt_pipeline.student_pipeline import run_student_pipeline
from api.utils.storage import next_student_id, save_student_json, append_student_csv, get_student_json
from api.utils.pdf_wrapper import generate_student_pdf

# Initialize FastAPI app
app = FastAPI(
    title="Digital Twin AI API",
    description="API for generating student digital twins based on input form data.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/create_digital_twin", summary="Create a new student digital twin")
def create_digital_twin(form: StudentForm):
    try:
        # 1) Generate Student ID
        student_id = next_student_id()
        
        # 2) Run AI Pipeline
        student_payload = form.dict()
        # Add ID to payload
        student_payload["student_id"] = student_id
        
        digital_twin = run_student_pipeline(student_payload)
        
        # 3) save student raw input and append csv
        save_student_json(student_id, student_payload)
        append_student_csv(student_id, student_payload)

        # 4) generate PDF (synchronous for demo)
        pdf_path = generate_student_pdf(student_id, digital_twin)
        # convert to URL path for dashboard assuming static serving from /pdf_reports
        pdf_url = os.path.join("/pdf_reports", os.path.basename(pdf_path)).replace("\\", "/")

        # 5) add links and metadata to result
        result = {
            "student_id": student_id,
            "digital_twin": digital_twin,
            "pdf_path": pdf_path,
            "pdf_url": pdf_url,
            "dashboard_url": f"{os.environ.get('DASHBOARD_BASE','http://localhost:8501')}/pages/Dashboard?student={student_id}"
        }
        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

@app.get("/get_digital_twin/{student_id}", summary="Get student digital twin")
def get_digital_twin(student_id: str) -> Dict[str, Any]:
    """
    Retrieve an existing digital twin by Student ID.
    """
    data = get_student_json(student_id)
    if not data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Re-run pipeline to get digital twin data
        digital_twin = run_student_pipeline(data)
        
        return {
            "student_id": student_id,
            "digital_twin": digital_twin,
            "input_summary": data
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error regenerating twin: {str(e)}")

# Mount static files for PDF serving
PDF_DIR = os.environ.get("PDF_OUTPUT_DIR", "./pdf_reports")
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)
app.mount("/pdf_reports", StaticFiles(directory=PDF_DIR), name="pdf_reports")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
