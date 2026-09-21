from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import split_text


pdf_path = "data/resume.pdf"

text = load_pdf(pdf_path)

print("Characters extracted:", len(text))

chunks = split_text(text)

print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks[:3]):
    print("\n--- CHUNK", i + 1, "---")
    print(chunk.page_content)