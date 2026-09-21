import streamlit as st

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import split_text
from src.retrieval.vector_store import create_vector_store
from src.analysis.job_analyzer import extract_requirements
from src.analysis.match_pipeline import analyze_requirements


st.set_page_config(
    page_title="JobFit RAG",
    page_icon="💼",
    layout="wide"
)

st.title("💼 JobFit RAG")
st.write("Resume & Job Description Matching Assistant")

st.divider()

# -----------------------------
# Resume Upload
# -----------------------------

st.subheader("📄 Upload Resume")

resume_file = st.file_uploader(
    "Upload your resume as a PDF",
    type=["pdf"]
)

st.divider()

# -----------------------------
# Job Description
# -----------------------------

st.subheader("💼 Job Description")

job_description = st.text_area(
    "Paste the job description below",
    height=300,
    placeholder="Paste the job description here..."
)

st.divider()

# -----------------------------
# Analyze
# -----------------------------

if st.button("🔍 Analyze Job Fit", type="primary"):

    if resume_file is None:
        st.warning("Please upload your resume.")

    elif not job_description.strip():
        st.warning("Please enter a job description.")

    else:

        with st.spinner("Analyzing your resume and job description..."):

            # Save uploaded PDF temporarily
            with open("uploaded_resume.pdf", "wb") as file:
                file.write(resume_file.getbuffer())

            # Load resume
            resume_text = load_pdf("uploaded_resume.pdf")

            # Split resume into chunks
            resume_documents = split_text(resume_text)

            # Create vector store
            vector_store = create_vector_store(resume_documents)

            # Extract job requirements
            requirements = extract_requirements(
                job_description
            )

            # Analyze requirements
            results, score = analyze_requirements(
                requirements,
                vector_store,
                resume_documents
            )

        st.success("Analysis complete!")

        st.divider()

        # -----------------------------
        # Match Score
        # -----------------------------

        st.subheader("📊 Match Score")

        st.metric(
            label="Overall Job Fit",
            value=f"{score:.1f}%"
        )

        st.divider()

        # -----------------------------
        # Requirement Results
        # -----------------------------

        st.subheader("📋 Requirement Analysis")

        for result in results:

            status = result["status"]

            if status == "SUPPORTED":
                icon = "✅"

            elif status == "PARTIAL":
                icon = "🟡"

            else:
                icon = "❌"

            with st.expander(
                f"{icon} {result['requirement']} — {status}"
            ):

                st.write(
                    f"**Category:** {result['category']}"
                )

                st.write(
                    f"**Explanation:** {result['explanation']}"
                )

                st.write("**Resume Evidence:**")

                st.code(
                    result["evidence"]
                )