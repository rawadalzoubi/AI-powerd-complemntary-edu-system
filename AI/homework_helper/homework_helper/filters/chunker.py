import logging
from typing import List, Dict, Any
import gc
import sys

logger = logging.getLogger(__name__)

class Chunker:
    """Splits text into chunks for processing."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, max_chunks: int = 1000):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            max_chunks: Maximum number of chunks to create
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunks = max_chunks
        logger.info(f"Initialized chunker with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, max_chunks={max_chunks}")
    
    def process(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of dictionaries containing document data
                      with keys: id, file_name, text
            
        Returns:
            List of text chunks with metadata
        """
        if not documents:
            logger.warning("No documents provided to chunker")
            return []
        
        all_chunks = []
        
        for doc in documents:
            try:
                text = doc['text']
                if not text:
                    logger.warning(f"Empty text in document {doc.get('file_name', 'unknown')}")
                    continue
                
                # Clean up the text
                text = text.strip()
                logger.info(f"Processing text of length {len(text)} characters from {doc.get('file_name', 'unknown')}")
                
                # If text is too long, truncate it
                max_text_length = self.chunk_size * self.max_chunks
                if len(text) > max_text_length:
                    logger.warning(f"Text too long ({len(text)} chars), truncating to {max_text_length} chars")
                    text = text[:max_text_length]
                
                # Split into chunks
                chunks = []
                start = 0
                total_length = len(text)
                
                while start < total_length and len(chunks) < self.max_chunks:
                    # Get chunk of text
                    end = min(start + self.chunk_size, total_length)
                    chunk_text = text[start:end]
                    
                    # Create chunk with metadata
                    chunk = {
                        "text": chunk_text,
                        "start": start,
                        "end": end,
                        "file_name": doc.get('file_name', 'unknown'),
                        "doc_id": doc.get('id')
                    }
                    chunks.append(chunk)
                    
                    # Move to next chunk with overlap
                    start = end - self.chunk_overlap
                    
                    # Log progress
                    if len(chunks) % 100 == 0:
                        logger.info(f"Created {len(chunks)} chunks so far...")
                    
                    # Force garbage collection periodically
                    if len(chunks) % 500 == 0:
                        gc.collect()
                        logger.debug(f"Memory usage: {sys.getsizeof(chunks) / 1024 / 1024:.2f} MB")
                
                logger.info(f"Successfully split document into {len(chunks)} chunks")
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.error(f"Error processing document {doc.get('file_name', 'unknown')}: {str(e)}")
                continue
        
        return all_chunks 