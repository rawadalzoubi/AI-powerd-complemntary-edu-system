import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# --- باقي كود main.py يبدأ من هنا ---
import logging
from homework_helper.config import Config
# ... إلخ
import logging
from homework_helper.config import Config
from homework_helper.filters.mysql_loader import MySQLLoader
from homework_helper.filters.pdf_parser import PDFParser
from homework_helper.filters.chunker import Chunker
from homework_helper.filters.embedder import create_embedder
from homework_helper.filters.vector_store import VectorStore
from homework_helper.filters.retriever import Retriever
from homework_helper.filters.llm_answer import create_llm_answer
from homework_helper.pipeline import Pipeline

# FastAPI and Pydantic imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- FastAPI App Setup ---
app = FastAPI(title="Homework Helper API", version="0.1.0")

# CORS Middleware Configuration
origins = [
    "http://localhost",
    "http://localhost:5173",  # Assuming frontend runs here
    # Add any other origins your frontend might be served from
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"], # Specify methods, or use ["*"]
    allow_headers=["*"], # Specify headers, or use ["*"]
)

# --- Pydantic Models for API ---
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    relevant_chunks_count: int

# --- Global variables for QA pipeline (initialized at startup) ---
config_global: Config = None
retriever_instance_global: Retriever = None
llm_instance_global: any = None # Type hint for the LLM instance
vector_store_instance_global: VectorStore = None

# --- QA Pipeline Initialization Function ---
def setup_qa_pipeline_globals():
    global config_global, retriever_instance_global, llm_instance_global, vector_store_instance_global
    try:
        logger.info("Initializing QA pipeline for API...")
        config_global = Config()
        config_global.validate()

        indexing_pipeline = build_indexing_pipeline(config_global)
        logger.info("Building document index for API...")
        vector_store_instance_global = indexing_pipeline.run()
        if not isinstance(vector_store_instance_global, VectorStore):
            logger.error("Indexing pipeline did not return a valid VectorStore instance. API cannot function correctly.")
            raise RuntimeError("Failed to initialize VectorStore for API.")
        logger.info("Document index built (or VectorStore initialized) successfully for API!")

        qa_components = build_qa_pipeline(config_global, vector_store_instance_global)
        retriever_instance_global = qa_components['retriever']
        llm_instance_global = qa_components['llm']
        logger.info("QA Pipeline is ready for API.")
    except Exception as e:
        logger.error(f"API setup error during QA pipeline initialization: {e}", exc_info=True)
        # This error will prevent the app from starting correctly if not handled by FastAPI's startup event.
        raise RuntimeError(f"Critical error during QA pipeline setup: {e}")

# --- FastAPI Events ---
@app.on_event("startup")
async def startup_event():
    """
    Run QA pipeline initialization at application startup.
    """
    try:
        setup_qa_pipeline_globals()
    except Exception as e:
        # Log and exit if startup fails critically
        logger.critical(f"Failed to initialize QA pipeline during startup: {e}", exc_info=True)
        # Depending on Uvicorn/FastAPI version, exiting might need a more forceful approach
        # or reliance on process managers to restart.
        # For now, logging critical error. The app might start in a broken state or fail to start.
        # Uvicorn should ideally not start the server if startup events raise unhandled exceptions.
        raise # Re-raise to signal critical failure

# --- API Endpoints ---
@app.post("/ask_question", response_model=AnswerResponse)
async def ask_question_endpoint(request: QuestionRequest):
    """
    API endpoint to ask a question to the Homework Helper.
    """
    if not retriever_instance_global or not llm_instance_global or not config_global:
        logger.error("API called before QA pipeline is ready.")
        raise HTTPException(status_code=503, detail="Service Unavailable: QA pipeline is not initialized.")

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        q_snippet = question[:100] # Simplified for logging
        logger.info(f"API - Processing question: '{q_snippet}...'")
        relevant_chunks = retriever_instance_global.process(question, k=config_global.top_k_results)

        if not relevant_chunks:
            logger.info("API - No relevant chunks found. Generating answer without specific context.")
            answer = llm_instance_global.generate_answer(question, []) 
            return AnswerResponse(answer=answer, relevant_chunks_count=0)

        logger.info(f"API - Retrieved {len(relevant_chunks)} relevant chunks.")
        answer = llm_instance_global.generate_answer(question, relevant_chunks)
        return AnswerResponse(answer=answer, relevant_chunks_count=len(relevant_chunks))

    except Exception as e:
        logger.error(f"API - Error processing question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while processing your question.")

# --- Original functions (build_indexing_pipeline, build_qa_pipeline) ---
def build_indexing_pipeline(config: Config):
    """Build pipeline for indexing documents."""
    embedder_type = config.embedder_type
    embedder_kwargs = {"model_name": config.embedder_model}
    if embedder_type == "ollama":
        embedder_kwargs["base_url"] = config.ollama_base_url
    elif embedder_type == "huggingface":
        if hasattr(config, 'huggingface_device') and config.huggingface_device:
            embedder_kwargs["device"] = config.huggingface_device
        if hasattr(config, 'embedder_trust_remote_code'):
            embedder_kwargs["trust_remote_code"] = config.embedder_trust_remote_code
        # يمكنك أيضًا تمرير huggingface_api_key هنا إذا كان الـ embedder يحتاجه (نماذج تضمين مقيدة)
        # if hasattr(config, 'huggingface_api_key') and config.huggingface_api_key:
        #     embedder_kwargs["token"] = config.huggingface_api_key
            
    return Pipeline([
        MySQLLoader(config.mysql_config),
        PDFParser(),
        Chunker(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap, max_chunks=config.max_chunks),
        create_embedder(embedder_type, **embedder_kwargs),
        VectorStore()
    ])

def build_qa_pipeline(config: Config, vector_store_instance: VectorStore):
    """Build pipeline for question answering."""
    embedder_type = config.embedder_type
    embedder_kwargs_query = {"model_name": config.embedder_model}
    if embedder_type == "ollama":
        embedder_kwargs_query["base_url"] = config.ollama_base_url
    elif embedder_type == "huggingface":
        if hasattr(config, 'huggingface_device') and config.huggingface_device:
            embedder_kwargs_query["device"] = config.huggingface_device
        if hasattr(config, 'embedder_trust_remote_code'):
            embedder_kwargs_query["trust_remote_code"] = config.embedder_trust_remote_code
        # يمكنك أيضًا تمرير huggingface_api_key هنا إذا كان الـ embedder يحتاجه
        # if hasattr(config, 'huggingface_api_key') and config.huggingface_api_key:
        #     embedder_kwargs_query["token"] = config.huggingface_api_key

    query_embedder = create_embedder(embedder_type, **embedder_kwargs_query)

    llm_type = config.llm_type
    # Populate llm_kwargs with all relevant attributes from config.
    # create_llm_answer will pick the ones it needs based on llm_type.
    llm_kwargs = {
        "model_name": config.llm_model_name_for_type, # Generic model name for ollama/hf
        "ollama_base_url": config.ollama_base_url,
        "huggingface_device": config.huggingface_device,
        "use_seq2seq": config.huggingface_llm_use_seq2seq,
        "huggingface_llm_torch_dtype_str": config.huggingface_llm_torch_dtype_str,
        "huggingface_api_key": config.huggingface_api_key,
        "replicate_api_token": config.replicate_api_token,
        "replicate_model_identifier": config.replicate_model_identifier,
        # Pass specific model names as well, create_llm_answer can use them if needed or ignore
        "ollama_llm_model": config.ollama_llm_model, 
        "huggingface_llm_model": config.huggingface_llm_model
    }

    # The create_llm_answer factory is now solely responsible for
    # selecting the appropriate arguments from llm_kwargs based on llm_type.
    # The previous if/elif/else block modifying llm_kwargs here is removed.
        
    return {
        'retriever': Retriever(query_embedder, vector_store_instance),
        'llm': create_llm_answer(llm_type, **llm_kwargs)
    }

def main():
    """Main entry point for the application (CLI version)."""
    try:
        config = Config()
        config.validate() 
        
        indexing_pipeline = build_indexing_pipeline(config)
        logger.info("Building document index...")
        vector_store_instance = indexing_pipeline.run()
        if not isinstance(vector_store_instance, VectorStore):
            logger.error("Indexing pipeline did not return a valid VectorStore instance. Exiting.")
            return

        logger.info("Document index built (or VectorStore initialized) successfully!")
        
        qa_components = build_qa_pipeline(config, vector_store_instance)
        retriever_instance = qa_components['retriever']
        llm_instance = qa_components['llm']

        logger.info("\nHomework Helper is ready! Type 'exit' to quit.")
        while True:
            question = input("\nYour question: ").strip()
            if not question:
                continue
            if question.lower() == 'exit':
                logger.info("Exiting Homework Helper.")
                break
            try:
                logger.info(f"Processing question: \"{question[:100]}...\"")
                relevant_chunks = retriever_instance.process(question, k=config.top_k_results)
                
                if not relevant_chunks:
                    print("No relevant information found in the indexed documents to answer this question.")
                    logger.info("No relevant chunks found.")
                    continue
                    
                logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks.")
                answer = llm_instance.generate_answer(question, relevant_chunks)
                print("\nAnswer:", answer)
                
            except Exception as e:
                logger.error(f"Error processing question: {e}", exc_info=True)
                print("Sorry, I encountered an error while processing your question.")
                
    except Exception as e:
        logger.error(f"Application startup error: {e}", exc_info=True)

if __name__ == "__main__":
    # main() # Original CLI execution

    # --- Start FastAPI server ---
    logger.info("Starting Homework Helper API server...")
    # Note: The startup_event will handle QA pipeline initialization.
    # If setup_qa_pipeline_globals() raises an unhandled exception during startup,
    # Uvicorn should ideally fail to start or report the error.
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except RuntimeError as e: # Catch specific RuntimeError from setup if it propagates here
        logger.critical(f"Failed to start API server due to runtime error in setup: {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"An unexpected error occurred while trying to start the Uvicorn server: {e}", exc_info=True)

# Ensure there's a newline at the end of the file if it's missing.