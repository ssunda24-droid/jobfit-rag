def create_semantic_index(documents):
    """Create a temporary Chroma index using FastEmbed's ONNX runtime."""
    try:
        from langchain_chroma import Chroma
        from langchain_community.embeddings import FastEmbedEmbeddings
    except ImportError as exc:
        raise RuntimeError(
            "Semantic retrieval needs FastEmbed and Chroma. "
            "Install them with: python -m pip install -r requirements-semantic-local.txt"
        ) from exc

    embeddings = FastEmbedEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=8,
        threads=1,
    )
    return Chroma.from_documents(documents=documents, embedding=embeddings)


# Keep the old factory name available for the legacy Streamlit app and scripts.
def create_vector_store(documents, persist_directory=None):
    return create_semantic_index(documents)
