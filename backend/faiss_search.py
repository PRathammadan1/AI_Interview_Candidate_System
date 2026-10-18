import faiss
import numpy as np

def create_faiss_index(vectors):
    vectors = np.array(vectors, dtype="float32")
    dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(vectors)

    return index

def search_faiss(index, query_vector, k=3):
        query_vector = np.array(
        [query_vector],
        dtype="float32"
    )

        distances, indices = index.search(
        query_vector,
        k
    )

        return distances, indices