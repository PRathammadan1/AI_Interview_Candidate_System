from langchain_ollama import OllamaEmbeddings


def create_embedding(chunks):
    embeddings = OllamaEmbeddings(
        model="embeddinggemma"
    )

    vectors = embeddings.embed_documents(chunks)

    return vectors
