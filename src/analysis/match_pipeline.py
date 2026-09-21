import time

from src.retrieval.retriever import retrieve_resume_evidence
from src.analysis.match_analyzer import analyze_match


def analyze_requirements(requirements, vector_store, resume_documents):

    results = []

    for category, items in requirements.items():

        for requirement in items:

            if category == "experience_requirements":

                # Experience requirements need the full resume
                # so the model can reason about employment dates.
                documents = resume_documents

            else:

                # Other requirements use semantic retrieval.
                documents = retrieve_resume_evidence(
                    vector_store,
                    requirement,
                    k=3
                )

            resume_evidence = "\n\n".join(
                document.page_content
                for document in documents
            )

            match = analyze_match(
                requirement=requirement,
                resume_evidence=resume_evidence
            )

            time.sleep(3)

            results.append({
                "category": category,
                "requirement": requirement,
                "status": match["status"],
                "explanation": match["explanation"],
                "evidence": resume_evidence
            })
                # Calculate deterministic match score
    total_requirements = len(results)

    supported = sum(
        1 for result in results
        if result["status"] == "SUPPORTED"
    )

    partial = sum(
        1 for result in results
        if result["status"] == "PARTIAL"
    )

    score = (
        (supported + 0.5 * partial) / total_requirements * 100
        if total_requirements > 0
        else 0
    )

    return results, score
