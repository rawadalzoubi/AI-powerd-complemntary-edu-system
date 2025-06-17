import os
import time
import logging
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer, models
import torch

logger = logging.getLogger(__name__)

class BaseEmbedder(ABC):
    """Abstract base class for text embedding generators."""
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text chunk."""
        pass
        
    def process(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process chunks by adding embeddings (default synchronous, one-by-one implementation)."""
        logger.info(f"Generating embeddings for {len(chunks)} chunks using BaseEmbedder.process...")
        for i, chunk in enumerate(chunks):
            try:
                embedding = self.generate_embedding(chunk["text"])
                chunk["embedding"] = embedding
                logger.debug(f"Generated embedding for chunk {i+1}/{len(chunks)}")
                # Basic throttling for synchronous one-by-one processing
                if (i + 1) % 10 == 0: # Log every 10, sleep a bit more rarely if needed.
                    logger.info(f"Processed {i+1}/{len(chunks)} chunks...")
                    # time.sleep(0.05) # Optional: if very CPU intensive and not IO bound
            except Exception as e:
                logger.error(
                    f"Error embedding chunk {i} (text: '{chunk.get('text','unknown')[:50]}...', "
                    f"file: {chunk.get('file_name','unknown')}): {e}"
                )
                # Decide if you want to raise, or assign None and continue
                chunk["embedding"] = None # Or raise e to stop processing
        return chunks

class OllamaEmbedder(BaseEmbedder):
    """Generates embeddings using an Ollama server via HTTP API."""
    def __init__(
        self,
        model_name: str = "nomic-embed-text", # Default to a common embedding model
        base_url: str = "http://localhost:11434",
        max_retries: int = 3,
        retry_delay: float = 1.0, # Initial delay in seconds
        batch_size: int = 32, # Number of texts to process in one logical batch for asyncio.gather
        max_concurrent: int = 1, # Max concurrent API calls to Ollama
    ):
        self.model_name = model_name
        self.embed_url = f"{base_url.rstrip('/')}/api/embeddings"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.batch_size = batch_size # How many embedding tasks to group for one `asyncio.gather`
        self.max_concurrent = max_concurrent # Controls the semaphore for concurrent HTTP requests
        logger.info(
            f"Initialized OllamaEmbedder with model: {model_name} at {self.embed_url}, "
            f"max_concurrent: {self.max_concurrent}, logical_batch_size: {self.batch_size}"
        )

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Synchronous wrapper for async embedding generation for a single text.
        Returns embedding or None if an error occurs.
        """
        try:
            return asyncio.run(self._generate_single_embedding_async(text))
        except Exception as e:
            logger.error(f"Failed to generate embedding synchronously for text '{text[:50]}...': {e}")
            return None

    async def _generate_single_embedding_async(self, text: str, session: Optional[aiohttp.ClientSession] = None) -> List[float]:
        """
        Generate embedding for a single text asynchronously.
        Manages its own session if one is not provided.
        """
        if session:
            return await self._api_call_with_retry(text, session)
        else:
            # Create a session for this single call if not provided
            async with aiohttp.ClientSession() as new_session:
                return await self._api_call_with_retry(text, new_session)

    async def _api_call_with_retry(self, text: str, session: aiohttp.ClientSession) -> List[float]:
        """Makes the actual API call to Ollama with retry logic."""
        current_delay = self.retry_delay
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                payload = {"model": self.model_name, "prompt": text}
                logger.debug(f"Attempt {attempt+1}: POST to {self.embed_url} with payload: {payload}")
                async with session.post(
                    self.embed_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60), # Increased timeout
                    headers={"Content-Type": "application/json"},
                    # ssl=False # Only if strictly necessary for localhost and http, usually not needed.
                                  # aiohttp handles http correctly.
                ) as resp:
                    logger.debug(f"Response status: {resp.status}, content-type: {resp.content_type}")
                    if resp.status == 200:
                        data = await resp.json()
                        if "embedding" not in data or not isinstance(data["embedding"], list):
                            logger.error(f"Invalid response structure from Ollama: 'embedding' key missing or not a list. Response: {data}")
                            raise KeyError(f"Ollama API response missing 'embedding' key or malformed. Data: {data}")
                        return data["embedding"]
                    else:
                        body = await resp.text()
                        logger.warning(
                            f"Ollama API request failed (Attempt {attempt+1}/{self.max_retries}) "
                            f"Status: {resp.status}, Body: {body}"
                        )
                        # Specific error handling for common issues
                        if resp.status == 404 and "model not found" in body.lower():
                            # If model not found, retrying won't help.
                            raise RuntimeError(f"Model '{self.model_name}' not found on Ollama server. {body}")
                        last_exception = RuntimeError(f"Ollama API request failed with status {resp.status}: {body}")
            
            except aiohttp.ClientConnectorError as e: # DNS or connection errors
                logger.warning(f"Connection error (Attempt {attempt+1}/{self.max_retries}): {e}")
                last_exception = e
            except aiohttp.ClientResponseError as e: # HTTP errors not caught by status check, e.g. non-200 that don't get a body.
                logger.warning(f"Client response error (Attempt {attempt+1}/{self.max_retries}): {e.status} {e.message}")
                last_exception = e
            except asyncio.TimeoutError as e: # Timeout for the request
                logger.warning(f"Request timed out (Attempt {attempt+1}/{self.max_retries}): {e}")
                last_exception = e
            except KeyError as e: # Specific error for missing 'embedding' key
                logger.error(f"Data format error from Ollama (Attempt {attempt+1}/{self.max_retries}): {e}")
                last_exception = e # Stop retrying if it's a format error likely to persist
                break 
            except Exception as e: # Catch other unexpected errors
                logger.error(f"Unexpected error during Ollama API call (Attempt {attempt+1}/{self.max_retries}): {e}")
                last_exception = e

            if attempt < self.max_retries - 1:
                logger.info(f"Retrying in {current_delay:.2f} seconds...")
                await asyncio.sleep(current_delay)
                current_delay = min(current_delay * 2, 30) # Exponential backoff, capped at 30s
            else:
                logger.error(f"Max retries ({self.max_retries}) reached for OllamaEmbedder. Last error: {last_exception}")
                if last_exception:
                    raise last_exception
                else: # Should not happen if loop completed
                    raise RuntimeError("Max retries reached for OllamaEmbedder with no specific exception recorded.")
        # This part should ideally not be reached if logic is correct, as success returns and failure raises.
        # Adding for safety in case of unexpected flow.
        raise RuntimeError("Failed to get embedding from Ollama after all retries and attempts.")


    async def _process_chunk_with_semaphore(
        self, chunk_data: Dict[str, Any], session: aiohttp.ClientSession, semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Wrapper to process a single chunk with semaphore control."""
        async with semaphore:
            try:
                embedding = await self._api_call_with_retry(chunk_data["text"], session)
                chunk_data["embedding"] = embedding
                logger.debug(f"Successfully embedded chunk (file: {chunk_data.get('file_name', 'N/A')})")
            except Exception as e:
                logger.error(
                    f"Failed to embed chunk (text: '{chunk_data.get('text','unknown')[:50]}...', "
                    f"file: {chunk_data.get('file_name', 'N/A')}): {e}"
                )
                chunk_data["embedding"] = None # Assign None if embedding fails for this chunk
            return chunk_data

    async def _process_chunks_async(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process chunks by adding embeddings in parallel, respecting max_concurrent."""
        logger.info(
            f"Asynchronously processing {len(chunks)} chunks with OllamaEmbedder (model: {self.model_name}). "
            f"Logical batch size: {self.batch_size}, Max concurrent API calls: {self.max_concurrent}."
        )
        
        results: List[Dict[str, Any]] = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create a single session for all operations within this method call
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(0, len(chunks), self.batch_size):
                logical_batch = chunks[i : i + self.batch_size]
                logger.debug(f"Creating tasks for logical batch {i//self.batch_size + 1} (size: {len(logical_batch)})")
                for chunk_item in logical_batch:
                    tasks.append(self._process_chunk_with_semaphore(chunk_item, session, semaphore))
            
            # asyncio.gather will run tasks concurrently, limited by the semaphore internally
            # and also by how many tasks are submitted at once if not all tasks are created before gather.
            # Here, all tasks are created first.
            
            # Process tasks, potentially in groups if you want to log progress for very large lists
            # For simplicity, gather all tasks. `return_exceptions=True` is crucial.
            processed_task_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results. `processed_task_results` will contain the modified chunk dicts or exceptions.
        # Since `_process_chunk_with_semaphore` returns the chunk_data (modified or with embedding=None),
        # we don't need to map back based on original index if all tasks succeed or handle errors by returning chunk_data.
        # However, if an exception was returned by gather, that specific task failed more severely.
        
        final_processed_chunks = []
        for i, result_or_exc in enumerate(processed_task_results):
            original_chunk_index = i # This assumes tasks were added in order of chunks
            if isinstance(result_or_exc, Exception):
                logger.error(f"Task for chunk index {original_chunk_index} failed with an unhandled exception: {result_or_exc}")
                # Original chunk data might be lost if we don't have a way to retrieve it.
                # The current `_process_chunk_with_semaphore` returns the chunk, so this path is less likely for app errors.
                # This would be for asyncio errors or if `_process_chunk_with_semaphore` itself raised an unhandled one.
                # We will add the original chunk with embedding set to None.
                failed_chunk = chunks[original_chunk_index].copy() # Get original chunk
                failed_chunk["embedding"] = None
                final_processed_chunks.append(failed_chunk)
            elif isinstance(result_or_exc, dict):
                final_processed_chunks.append(result_or_exc) # This is the (potentially modified) chunk_data
            else:
                logger.warning(f"Unexpected item in asyncio.gather results for chunk index {original_chunk_index}: {result_or_exc}")
                # Add original chunk with embedding as None
                unexpected_chunk = chunks[original_chunk_index].copy()
                unexpected_chunk["embedding"] = None
                final_processed_chunks.append(unexpected_chunk)
        
        if len(final_processed_chunks) != len(chunks):
            logger.warning(f"Mismatch in processed chunks count. Expected {len(chunks)}, got {len(final_processed_chunks)}. This may indicate an issue.")

        return final_processed_chunks # Return the list of chunks with embeddings (or None for errors)

    def process(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Override of BaseEmbedder.process to use asynchronous batch processing.
        """
        logger.info(f"Processing {len(chunks)} chunks with OllamaEmbedder (sync call to async backend)")
        # Ensure an event loop is running or run in a new one
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # If called from an async context, you might need to create a task
                # For simplicity, we'll assume this is called from sync code for now.
                # This can be tricky. `asyncio.run` cannot be called when a loop is already running.
                # A common pattern is to use `nest_asyncio` if you must call `asyncio.run` from an async context,
                # or to make the calling code `await` this method if it's async.
                # For now, let's assume the calling context is synchronous.
                # If it's truly async, this `process` method should be `async def process`.
                logger.warning("OllamaEmbedder.process called while an event loop is already running. "
                               "Consider making the calling code await _process_chunks_async directly if possible.")
                # Fallback or specific handling needed here. One option:
                # future = asyncio.ensure_future(self._process_chunks_async(chunks))
                # return loop.run_until_complete(future) # This might still have issues.
                # For now, we stick to asyncio.run(), which expects no running loop.
                # This implies this `process` method is the entry point from sync code.
                pass # Let asyncio.run handle it or raise error
        except RuntimeError: # No running event loop
            pass # This is expected if called from purely synchronous code

        return asyncio.run(self._process_chunks_async(chunks))


class HuggingFaceEmbedder(BaseEmbedder):
    """
    Generates text embeddings using a HuggingFace SentenceTransformer model.
    """
    def __init__(
        self,
        model_name: str,
        device: Optional[str] = None, # Allow device to be optional
        trust_remote_code: bool = False,
        **other_model_kwargs
    ):
        """
        Initializes the HuggingFace SentenceTransformer model.
        Args:
            model_name (str): The name of the Sentence Transformer model from HuggingFace.
            device (str, optional): The device to run the model on ('cpu', 'cuda'). 
                                    If None, automatically detects CUDA.
            trust_remote_code (bool): Whether to trust remote code for the model.
            **other_model_kwargs: Other keyword arguments for from_pretrained.
        """
        # Auto-detect device if not provided
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"No device specified, automatically selected: {self.device}")

        self.model_name = model_name
        self.trust_remote_code = trust_remote_code
        self.other_model_kwargs = other_model_kwargs

        logger.info(
            f"Loading SentenceTransformer model: {model_name} on device: {self.device} "
            f"with trust_remote_code={trust_remote_code} (explicit module construction)"
        )
        try:
            # Create the model using the recommended explicit module creation
            word_embedding_model = models.Transformer(
                model_name_or_path=model_name,
                **other_model_kwargs
            )
            # Apply pooling layer
            pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
            # Create the final SentenceTransformer model
            self.model = SentenceTransformer(
                modules=[word_embedding_model, pooling_model],
                device=self.device,
                trust_remote_code=self.trust_remote_code
            )
            logger.info(f"Model {model_name} loaded successfully on device {self.device} (explicit module setup).")
        except Exception as e:
            logger.error(
                f"Failed to load SentenceTransformer model {model_name} on device {self.device}. "
                f"Error: {e}",
                exc_info=True
            )
            raise  # Re-raise exception to prevent using a failed model

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text chunk."""
        logger.debug(f"Generating HuggingFace embedding for text: '{text[:50]}...'")
        try:
            # .encode() can take a single string or a list of strings
            emb = self.model.encode(text, convert_to_numpy=True) 
            return emb.tolist()
        except Exception as e:
            logger.error(f"Error generating HuggingFace embedding: {e}")
            raise # Or return None / handle error appropriately

    def process(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process chunks by adding embeddings in batch."""
        if not chunks:
            return []
        logger.info(f"Generating HuggingFace embeddings for {len(chunks)} chunks (model: {self.model_name})")
        
        texts = [chunk["text"] for chunk in chunks]
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True, # Returns numpy arrays
                show_progress_bar=True, # Show a progress bar during encoding
                batch_size=32 # Internal batch size for the model's own processing
            )
            logger.info(f"Successfully encoded {len(texts)} texts into embeddings.")
        except Exception as e:
            logger.error(f"Batch encoding failed with HuggingFace model: {e}")
            # Assign None to all embeddings in case of batch failure or re-raise
            for chunk in chunks:
                chunk["embedding"] = None
            raise # Or return chunks with None embeddings

        for chunk, emb in zip(chunks, embeddings):
            chunk["embedding"] = emb.tolist()
            
        return chunks

def create_embedder(embedder_type: str, **kwargs) -> BaseEmbedder:
    """
    Factory to create an embedder.
    
    Args:
        embedder_type: "ollama" or "huggingface"
        **kwargs: Additional arguments for the specific embedder
        
    Returns:
        An instance of BaseEmbedder
        
    Example usage:
        # For Ollama (ensure Ollama server is running and model is pulled e.g. "nomic-embed-text"):
        # ollama_embedder = create_embedder("ollama", model_name="nomic-embed-text", base_url="http://localhost:11434")
        # results = ollama_embedder.process([{"text": "Hello from Ollama", "file_name": "test1"}])
        
        # For HuggingFace:
        # hf_embedder = create_embedder("huggingface", model_name="sentence-transformers/all-MiniLM-L6-v2")
        # results = hf_embedder.process([{"text": "Hello from HuggingFace", "file_name": "test2"}])
    """
    logger.info(f"Creating embedder of type: {embedder_type} with kwargs: {kwargs}")
    if embedder_type == "ollama":
        return OllamaEmbedder(**kwargs)
    elif embedder_type == "huggingface":
        return HuggingFaceEmbedder(**kwargs)
    else:
        logger.error(f"Unknown embedder type requested: {embedder_type}")
        raise ValueError(f"Unknown embedder type: {embedder_type}")

# Example usage (uncomment to test, ensure necessary setup e.g. Ollama server running)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    test_chunks = [
        {"text": "This is the first test sentence for embedding.", "file_name": "doc1.txt", "id": "chunk1"},
        {"text": "Another piece of text to see how embeddings are generated.", "file_name": "doc1.txt", "id": "chunk2"},
        {"text": "A third example, short and sweet.", "file_name": "doc2.txt", "id": "chunk3"},
        {"text": "مرحباً بالعالم، هذه جملة باللغة العربية.", "file_name": "doc3.txt", "id": "chunk4"},
    ]

    # Test HuggingFace Embedder
    logger.info("--- Testing HuggingFaceEmbedder ---")
    try:
        hf_embedder = create_embedder("huggingface", model_name="sentence-transformers/all-MiniLM-L6-v2")
        # Test single embedding
        # single_hf_emb = hf_embedder.generate_embedding("Test single HuggingFace.")
        # if single_hf_emb:
        # logger.info(f"Single HF embedding dim: {len(single_hf_emb)}")
        
        hf_results = hf_embedder.process(test_chunks[:]) # Process a copy
        for res_chunk in hf_results:
            embedding_preview = res_chunk.get("embedding")
            if embedding_preview:
                logger.info(f"HF Chunk ID {res_chunk.get('id')}: Embedding dim {len(embedding_preview)}, Preview: {embedding_preview[:3]}...")
            else:
                logger.warning(f"HF Chunk ID {res_chunk.get('id')}: No embedding generated.")
    except Exception as e:
        logger.error(f"Error during HuggingFaceEmbedder test: {e}", exc_info=True)

    logger.info("\n--- Testing OllamaEmbedder ---")
    logger.info("Ensure your Ollama server is running and the model (e.g., 'nomic-embed-text') is pulled.")
    logger.info("Example: `ollama pull nomic-embed-text`")
    try:
        # Make sure to use an actual embedding model name that you have pulled in Ollama
        ollama_embedder = create_embedder(
            "ollama", 
            model_name="nomic-embed-text", # or "mistral" if you know it works for embeddings AND it's pulled
            max_concurrent=2, # Lower concurrency for local testing if needed
            batch_size=2      # Smaller logical batch size for testing
        )
        
        # Test single embedding
        # single_ollama_emb = ollama_embedder.generate_embedding("Test single Ollama.")
        # if single_ollama_emb:
        #     logger.info(f"Single Ollama embedding dim: {len(single_ollama_emb)}")
        # else:
        #     logger.warning("Failed to get single Ollama embedding.")

        ollama_results = ollama_embedder.process(test_chunks[:]) # Process a copy
        for res_chunk in ollama_results:
            embedding_preview = res_chunk.get("embedding")
            if embedding_preview:
                logger.info(f"Ollama Chunk ID {res_chunk.get('id')}: Embedding dim {len(embedding_preview)}, Preview: {embedding_preview[:3]}...")
            else:
                logger.warning(f"Ollama Chunk ID {res_chunk.get('id')}: No embedding generated.")
    except Exception as e:
        logger.error(f"Error during OllamaEmbedder test: {e}", exc_info=True)