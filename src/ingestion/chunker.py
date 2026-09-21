from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=[
            "\n\n",
            "\n",
            "●",
            ". ",
            " ",
            ""
        ]
    )

    return splitter.create_documents([text])