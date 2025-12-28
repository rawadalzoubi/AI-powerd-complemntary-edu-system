from abc import ABC, abstractmethod

class BasePipeline(ABC):
    """
    Base class for all processing pipelines (Text, Image, Video).
    Ensures a consistent interface for full and incremental indexing.
    """
    def __init__(self, config):
        self.config = config
        self.vectorstore = None
        self.retriever = None

    @abstractmethod
    def run(self, files_to_process=None):
        """
        Execute the pipeline to ingest and index data.
        
        Args:
            files_to_process (list, optional): List of specific file paths to process.
                                               If None, the pipeline should process all available files.
                                               If provided, it should perform an incremental update (merge).
        """
        pass
    
    @abstractmethod
    def load_index(self):
        """Load the pre-built index from disk."""
        pass

    @abstractmethod
    def search(self, query):
        """Search the index."""
        pass