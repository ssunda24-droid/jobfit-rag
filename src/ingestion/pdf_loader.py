import pymupdf


def load_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""

    document = pymupdf.open(file_path)

    pages = []

    for page in document:
        pages.append(page.get_text())

    document.close()

    return "\n".join(pages)