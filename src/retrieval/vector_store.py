from langchain_chroma import Chroma


def create_vector_store(documents, persist_directory="chroma_db"):
    # Load the heavyweight ML stack on the first analysis request, not during
    # API startup. This lets the web service bind its port before loading Torch.
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    return vector_store
