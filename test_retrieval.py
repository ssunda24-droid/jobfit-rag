from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import split_text
from src.retrieval.vector_store import create_vector_store


PDF_PATH = "data/resume.pdf"


# 1. Load resume
text = load_pdf(PDF_PATH)

# 2. Split into chunks
documents = split_text(text)

print(f"Created {len(documents)} chunks")


# 3. Create vector database
vector_store = create_vector_store(documents)

print("Vector store created!")


# 4. Search the resume
query = "What experience does the candidate have with React?"

results = vector_store.similarity_search(query, k=3)


# 5. Display retrieved chunks
print("\n===== RETRIEVED RESUME EVIDENCE =====")

for i, document in enumerate(results):
    print(f"\n--- Result {i + 1} ---")
    print(document.page_content)