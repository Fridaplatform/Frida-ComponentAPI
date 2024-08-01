import faiss
from faiss.swigfaiss_avx2 import IndexFlatL2
import numpy as np
from typing import List


def create_faiss_index(dimensions: int = 1536) -> IndexFlatL2:
    """
    Creates a FAISS index for L2 distance (Euclidean distance).

    Args:
        dimensions (int): The dimensionality of the vectors to be indexed.

    Returns:
        IndexFlatL2: The FAISS index object.
    """
    return faiss.IndexFlatL2(dimensions)


def add_embeddings_to_index(index: IndexFlatL2, embeddings_array: np.ndarray) -> None:
    """
    Adds embeddings to the FAISS index.

    Args:
        index (IndexFlatL2): The FAISS index object.
        embeddings_array (np.ndarray): The array of embeddings to add.
    """
    index.add(embeddings_array)


def search_embeddings(embeddings: List[List[float]], query_embedding: List[float], k: int = 1) -> List[List[int]]:
    """
    Searches for the nearest neighbors of a query embedding in the FAISS index.

    Args:
        embeddings (List[List[float]]): List of embeddings to be indexed.
        query_embedding (List[float]): The query embedding to search for.
        k (int): The number of nearest neighbors to return.

    Returns:
        List[List[int]]: List of indices of the nearest neighbors.
    """
    embeddings_array = prepare_embeddings_array(embeddings)
    index = create_faiss_index(dimensions=embeddings_array.shape[1])
    add_embeddings_to_index(index=index, embeddings_array=embeddings_array)
    query_array = np.array([query_embedding], dtype='float32')
    _, result_indices = index.search(query_array, k)
    index.reset()  # TODO: Reset only if needed
    return result_indices


def prepare_embeddings_array(embeddings: List[List[float]]) -> np.ndarray:
    """
    Prepares the embeddings list for indexing by converting it into a numpy array.

    Args:
        embeddings (List[List[float]]): The list of embeddings to prepare.

    Returns:
        np.ndarray: The numpy array of embeddings.
    """
    return np.array(embeddings, dtype='float32')
