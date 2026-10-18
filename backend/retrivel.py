import faiss
import pickle

from backend.embedding import create_embedding
from backend.faiss_search import search_faiss


_index = None
_chunks = None


def reload_index():
    """Upload ke baad call karo, taaki naya resume memory mein load ho."""
    global _index, _chunks

    _index = faiss.read_index("faiss_index/index.faiss")

    with open("faiss_index/chunks.pkl", "rb") as f:
        _chunks = pickle.load(f)


def retrieve(query, k=3):

    # Pehli baar (ya reload ke baad) data load karo
    if _index is None or _chunks is None:
        reload_index()

    # Question ka embedding banao
    query_vector = create_embedding([query])[0]

    # FAISS se similar chunks ke indices nikalo
    distances, indices = search_faiss(
        _index,
        query_vector,
        k
    )

    # Indices ko actual text chunks mein convert karo
    results = []

    for i in indices[0]:
        # FAISS kam chunks hone par -1 de sakta hai, usko skip karo
        if 0 <= i < len(_chunks):
            results.append(_chunks[i])

    return results