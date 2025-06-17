from typing import List, Dict, Any
from .embedder import create_embedder
from .vector_store import VectorStore

class Retriever:
    """Filter to retrieve relevant chunks for a question using an embedder and vector store."""
    
    def __init__(self, embedder, vector_store: VectorStore):
        """
        Initialize the retriever.
        
        Args:
            embedder (Embedder): An initialized Embedder instance.
            vector_store (VectorStore): An initialized and processed VectorStore instance.
        """
        self.embedder = embedder
        self.vector_store = vector_store

    def process(self, question: str, k: int = 5) -> List[Dict]:
        """
        Process a question by embedding it and then searching the vector store for relevant chunks.
        
        Args:
            question (str): The user's question.
            k (int): The number of top relevant chunks to retrieve.
            
        Returns:
            List[Dict]: A list of relevant chunk dictionaries. Returns empty if error or no results.
        """
        if not question or not isinstance(question, str):
            print("Invalid question provided to retriever.")
            return []

        # Embed the question. Embedder.process expects a list of dicts.
        # The embedder adds an "embedding" key to the dict.
        question_dict = {"text": question}
        embedded_question_list = self.embedder.process([question_dict])
        
        if not embedded_question_list or not embedded_question_list[0].get("embedding"):
            print("Failed to generate embedding for the question.")
            return []
            
        query_embedding = embedded_question_list[0]["embedding"]
        
        # Search for similar chunks in the vector store
        relevant_chunks = self.vector_store.search(query_embedding, k)
        return relevant_chunks 