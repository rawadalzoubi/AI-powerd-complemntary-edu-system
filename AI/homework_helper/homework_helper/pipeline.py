from typing import List, Any, Callable

class Pipeline:
    """A generic pipeline to process data through a series of filter objects."""
    
    def __init__(self, filters: List[Any]):
        """
        Initialize the pipeline with a list of filter instances.
        Each filter instance must have a 'process' method.
        
        Args:
            filters (List[Any]): Ordered list of filter instances.
        """
        self.filters = filters

    def run(self, initial_data: Any = None) -> Any:
        """
        Run the initial data through all filters in the pipeline sequentially.
        
        Args:
            initial_data (Any): The input data for the first filter.
            
        Returns:
            Any: The processed data after passing through all filters, or None if an error occurs.
        """
        data = initial_data
        for i, filter_instance in enumerate(self.filters):
            try:
                # Check if the filter_instance has a 'process' method
                if not hasattr(filter_instance, 'process') or not callable(getattr(filter_instance, 'process')):
                    print(f"Error: Filter {type(filter_instance).__name__} at step {i+1} does not have a callable 'process' method.")
                    return None
                
                print(f"Pipeline: Executing filter {type(filter_instance).__name__} (Step {i+1}/{len(self.filters)})... ")
                data = filter_instance.process(data)
                # If a filter returns None and it's not the VectorStore (which can return self), 
                # it might indicate an issue or an intended stop, but we'll let it propagate for now.
                # Specific error handling or conditional stops could be added here if needed.
                print(f"Pipeline: Filter {type(filter_instance).__name__} completed.")

            except Exception as e:
                print(f"Error during pipeline execution at filter {type(filter_instance).__name__} (Step {i+1}): {e}")
                import traceback
                traceback.print_exc() # Print full traceback for debugging
                return None # Stop pipeline on error
                
        print("Pipeline: All filters executed successfully.")
        return data 