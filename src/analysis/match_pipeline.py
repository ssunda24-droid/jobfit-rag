from src.analysis.match_analyzer import analyze_matches
from src.retrieval.retriever import retrieve_resume_evidence

BATCH_SIZE = 10


def analyze_requirements(requirements, keyword_index, resume_documents):
    items = []
    for category, category_requirements in requirements.items():
        for requirement in category_requirements:
            if category == "experience_requirements":
                documents = resume_documents
            else:
                documents = retrieve_resume_evidence(keyword_index, requirement, k=3)
            items.append({
                "category": category,
                "requirement": requirement,
                "chunks": [document.page_content for document in documents],
            })

    matches = []
    for start in range(0, len(items), BATCH_SIZE):
        batch = items[start : start + BATCH_SIZE]
        matches.extend(
            analyze_matches([
                (item["requirement"], item["chunks"])
                for item in batch
            ])
        )

    results = []
    for item, match in zip(items, matches):
        results.append({
            "category": item["category"],
            "requirement": item["requirement"],
            "status": match["status"],
            "explanation": match["explanation"],
            "evidence": "\n\n".join(item["chunks"]),
        })

    total_requirements = len(results)
    supported = sum(result["status"] == "SUPPORTED" for result in results)
    partial = sum(result["status"] == "PARTIAL" for result in results)
    score = (
        (supported + 0.5 * partial) / total_requirements * 100
        if total_requirements
        else 0
    )
    return results, score
