import logging
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.analysis.job_analyzer import extract_requirements
from src.analysis.match_pipeline import analyze_requirements
from src.ingestion.chunker import split_text
from src.ingestion.pdf_loader import load_pdf
from src.retrieval.vector_store import create_vector_store


app = FastAPI(title="JobFit API")
logger = logging.getLogger(__name__)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in frontend_origin.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    if not resume.filename or Path(resume.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Please enter a job description.")

    pdf_bytes = resume.file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")
    if len(pdf_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Please upload a PDF smaller than 10 MB.")

    try:
        with tempfile.TemporaryDirectory(prefix="jobfit-") as temp_dir:
            pdf_path = Path(temp_dir) / "resume.pdf"
            pdf_path.write_bytes(pdf_bytes)
            resume_text = load_pdf(str(pdf_path))

            if not resume_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="No readable text was found. Please upload a text-based PDF.",
                )

            resume_documents = split_text(resume_text)
            vector_store = create_vector_store(
                resume_documents,
                persist_directory=str(Path(temp_dir) / "chroma"),
            )
            requirements = extract_requirements(job_description.strip())
            results, score = analyze_requirements(
                requirements,
                vector_store,
                resume_documents,
            )

        return {"score": score, "results": results}
    except HTTPException:
        raise
    except Exception as exc:
        # Keep provider and filesystem details out of the public response,
        # while recording the traceback in the API server logs for debugging.
        logger.exception("Resume analysis failed")
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please try again, and check the API server logs if it continues.",
        ) from exc
