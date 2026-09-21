def retrieve_resume_evidence(vector_store, requirement: str, k: int = 3):

    results = vector_store.similarity_search(
        requirement,
        k=k
    )

    unique_results = []
    seen = set()

    for document in results:

        content = document.page_content.strip()

        if content not in seen:
            seen.add(content)
            unique_results.append(document)

    return unique_results