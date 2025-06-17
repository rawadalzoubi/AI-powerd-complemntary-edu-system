import faiss
import numpy as np
from typing import List, Dict, Any, Optional

class VectorStore:
    """Filter to store and search vector embeddings using FAISS."""
    
    def __init__(self):
        """Initialize the vector store. Index and chunks are None until processed."""
        self.index: Optional[faiss.Index] = None
        self.chunks_with_embeddings: List[Dict] = []

    def process(self, chunks: List[Dict]) -> 'VectorStore':
        """
        Process the chunks by creating a FAISS index from their embeddings.
        Only chunks with valid embeddings are indexed.
        
        Args:
            chunks (List[Dict]): List of chunks, each expected to have an "embedding" key.
            
        Returns:
            VectorStore: Self, to allow for method chaining or direct use of the instance.
        """
        self.chunks_with_embeddings = [c for c in chunks if c.get("embedding") is not None and 
                                       isinstance(c["embedding"], list) and 
                                       len(c["embedding"]) > 0]
        
        if not self.chunks_with_embeddings:
            print("No valid chunks with embeddings to index.")
            self.index = None # Ensure index is None if no data
            return self
            
        embeddings = np.array([chunk["embedding"] for chunk in self.chunks_with_embeddings]).astype('float32')
        
        if embeddings.ndim == 1: # Handle case of single embedding
            embeddings = embeddings.reshape(1, -1)
            
        if embeddings.shape[0] == 0:
            print("Embeddings array is empty after filtering. Cannot build FAISS index.")
            self.index = None
            return self

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension) # Using L2 distance
        self.index.add(embeddings)
        
        print(f"FAISS index built successfully with {self.index.ntotal} vectors of dimension {dimension}.")
        return self

    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """
        Search the FAISS index for the k most similar chunks to the query_embedding.
        
        Args:
            query_embedding (List[float]): The embedding of the query.
            k (int): The number of top similar chunks to retrieve.
            
        Returns:
            List[Dict]: A list of the k most similar chunk dictionaries.
        """
        if self.index is None or self.index.ntotal == 0:
            print("Vector store is not initialized or empty. Cannot perform search.")
            return []
        if not query_embedding or not isinstance(query_embedding, list):
            print("Invalid query embedding provided.")
            return []
            
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Ensure k is not greater than the number of items in the index
        actual_k = min(k, self.index.ntotal)
        if actual_k == 0:
            return []

        distances, indices = self.index.search(query_vector, actual_k)
        
        # indices[0] contains the 0-indexed locations of the search results in self.chunks_with_embeddings
        results = [self.chunks_with_embeddings[i] for i in indices[0]]
        print(f"Retrieved {len(results)} chunks from vector store for the query.")
        return results 