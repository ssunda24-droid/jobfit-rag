from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import split_text
from src.retrieval.vector_store import create_vector_store
from src.retrieval.retriever import retrieve_resume_evidence
from src.analysis.match_analyzer import analyze_match


PDF_PATH = "data/resume.pdf"


# Load resume
text = load_pdf(PDF_PATH)

# Split resume into chunks
documents = split_text(text)

# Create vector store
vector_store = create_vector_store(documents)


# Job requirement
requirement = "Write unit and integration tests"


# Retrieve relevant resume evidence
results = retrieve_resume_evidence(
    vector_store,
    requirement,
    k=2
)


# Combine retrieved chunks
resume_evidence = "\n\n".join(
    document.page_content
    for document in results
)


# Analyze the match
result = analyze_match(
    requirement=requirement,
    resume_evidence=resume_evidence
)


print("\n===== JOB REQUIREMENT =====")
print(requirement)

print("\n===== RETRIEVED RESUME EVIDENCE =====")

for i, document in enumerate(results):
    print(f"\n--- Evidence {i + 1} ---")
    print(document.page_content)

print("\n===== MATCH RESULT =====")
print("Status:", result["status"])
print("Explanation:", result["explanation"])