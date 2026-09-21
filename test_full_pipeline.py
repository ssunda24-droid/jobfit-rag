from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import split_text
from src.retrieval.vector_store import create_vector_store

from src.analysis.job_analyzer import extract_requirements
from src.analysis.match_pipeline import analyze_requirements


# --------------------------------------------------
# 1. Load job description
# --------------------------------------------------

with open(
    "data/job_description/software_engineer.txt",
    "r"
) as file:

    job_description = file.read()


# --------------------------------------------------
# 2. Extract job requirements
# --------------------------------------------------

requirements = extract_requirements(
    job_description
)


# --------------------------------------------------
# 3. Load resume
# --------------------------------------------------

resume_text = load_pdf(
    "data/resume.pdf"
)


# --------------------------------------------------
# 4. Split resume into chunks
# --------------------------------------------------

resume_documents = split_text(
    resume_text
)


# --------------------------------------------------
# 5. Create vector store
# --------------------------------------------------

vector_store = create_vector_store(
    resume_documents
)


# --------------------------------------------------
# 6. Analyze all requirements
# --------------------------------------------------

results, score = analyze_requirements(
    requirements,
    vector_store,
    resume_documents
)

# --------------------------------------------------
# 7. Print results
# --------------------------------------------------

print("\n========================================")
print("        JOB FIT ANALYSIS")
print("========================================")


for result in results:

    print("\n----------------------------------------")

    print(
        f"Category: {result['category']}"
    )

    print(
        f"Requirement: {result['requirement']}"
    )

    print(
        f"Status: {result['status']}"
    )

    print(
        f"Explanation: {result['explanation']}"
    )

print("\n========================================")
print(f"        MATCH SCORE: {score:.1f}%")
print("========================================")