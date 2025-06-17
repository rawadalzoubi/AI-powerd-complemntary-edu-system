import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE" # أضف هذا السطر هنا
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any # Added Dict, Any
import uvicorn
# import os # تم استيراده في الأعلى بالفعل
import logging
from contextlib import asynccontextmanager

# استيراد Config و RAGSystem
from .config import Config # استيراد فئة Config
from .rag_core import RAGSystem

# إعداد التسجيل
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # يتم عادة في config.py أو main.py
logger = logging.getLogger(__name__)

# لا حاجة لـ load_dotenv() هنا بشكل مباشر إذا كانت Config تقوم بذلك عند إنشائها.

# متغير عام لنظام RAG
rag_system_instance: Optional[RAGSystem] = None # تم تغيير الاسم ليكون أوضح

@asynccontextmanager
async def lifespan(app: FastAPI):
    # بدء التشغيل
    global rag_system_instance
    logger.info("API starting up. Initializing RAGSystem...")
    try:
        # 1. إنشاء كائن Config
        config = Config()
        config.validate() # التحقق من صحة الإعدادات
        logger.info("Configuration loaded and validated.")

        # 2. تهيئة RAGSystem مع كائن Config
        rag_system_instance = RAGSystem(config=config)
        logger.info(f"RAG system initialized using Config. Embedder: {config.embedder_type}, LLM: {config.llm_type}")

        if rag_system_instance.vector_store and rag_system_instance.vector_store.index:
            logger.info(f"RAGSystem initialized. Indexed documents: {rag_system_instance.vector_store.index.ntotal}")
        else:
            # قد يكون الفهرس فارغًا إذا لم تكن هناك مستندات في قاعدة البيانات، وهذا ليس بالضرورة خطأ فادحًا عند البدء
            logger.warning("RAGSystem initialized, but vector store or index is missing/empty. This is normal if no data is in the DB.")
    except Exception as e:
        logger.error(f"Critical error during RAGSystem initialization: {e}", exc_info=True)
        rag_system_instance = None # تأكد من أنه None إذا فشلت التهيئة
    yield
    # إيقاف التشغيل
    logger.info("Shutting down RAG system...")
    rag_system_instance = None

app = FastAPI(
    title="Homework Helper RAG API",
    description="API to interact with the RAG system for question answering from documents.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (Cross-Origin Resource Sharing) middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح بجميع المصادر. للإنتاج، يجب تقييد هذا.
    allow_credentials=True,
    allow_methods=["*"], # يسمح بجميع الطرق (GET, POST, etc.)
    allow_headers=["*"],  # يسمح بجميع الترويسات
)

# --- Pydantic Models for Request and Response ---
class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = None # للسماح بتجاوز top_k من الإعدادات لكل طلب

class Source(BaseModel):
    file_name: str
    doc_id: Optional[str] = None # إضافة doc_id إذا كان متاحًا
    text_snippet: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Source]
    # error: Optional[str] = None # تمت إزالته، سيتم الاعتماد على رموز حالة HTTP للأخطاء

class StatusResponse(BaseModel):
    status: str
    indexed_documents: Optional[int] = None
    message: Optional[str] = None

# Dependency للحصول على نسخة RAG system
async def get_rag_system() -> RAGSystem:
    if rag_system_instance is None:
        logger.error("RAG system is not available. It might have failed during startup.")
        raise HTTPException(status_code=503, detail="Service Unavailable: RAG system failed to initialize or is not ready.")
    return rag_system_instance

# --- API Endpoints ---

@app.post("/ask_question", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest, current_rag_system: RAGSystem = Depends(get_rag_system)):
    logger.info(f"Received question: '{request.question[:50]}...'")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # استخدام request.top_k إذا تم توفيره، وإلا سيستخدم RAGSystem القيمة الافتراضية من Config
        k_to_use = request.top_k if request.top_k is not None else -1 # -1 ليعتمد RAGSystem على config
        result = current_rag_system.answer_question(request.question, k=k_to_use)

        logger.info(f"Successfully processed question: '{request.question[:50]}...'")
        return AnswerResponse(
            answer=result["answer"],
            sources=[
                Source(
                    file_name=source.get("file_name", "Unknown"),
                    doc_id=str(source.get("doc_id")) if source.get("doc_id") is not None else None,
                    text_snippet=source.get("text_snippet", "")
                )
                for source in result["sources"]
            ]
        )
    except HTTPException: # إعادة إثارة HTTPExceptions مباشرة
        raise
    except Exception as e:
        logger.error(f"Unexpected error answering question '{request.question[:50]}...': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

@app.post("/reindex", response_model=StatusResponse)
async def reindex_documents(current_rag_system: RAGSystem = Depends(get_rag_system)):
    logger.info("Received request to re-index documents.")
    try:
        current_rag_system.re_index() # تم تغيير الاسم ليتطابق مع RAGSystem
        indexed_count = current_rag_system.vector_store.index.ntotal if current_rag_system.vector_store and current_rag_system.vector_store.index else 0
        logger.info("Documents re-indexed successfully.")
        return StatusResponse(status="success", message="Documents re-indexed successfully.", indexed_documents=indexed_count)
    except Exception as e:
        logger.error(f"Error during re-indexing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to re-index documents: {str(e)}")

@app.get("/status", response_model=StatusResponse)
async def get_status(current_rag_system: RAGSystem = Depends(get_rag_system)): # استخدام current_rag_system
    logger.debug("Received status request.")
    if current_rag_system and current_rag_system.vector_store and current_rag_system.vector_store.index:
        return StatusResponse(
            status="RAG system initialized and running.",
            indexed_documents=current_rag_system.vector_store.index.ntotal
        )
    elif rag_system_instance:
         return StatusResponse(status="RAG system initialized, but index is not available or empty.", indexed_documents=0)
    else:
        return StatusResponse(status="RAG system not initialized or failed to start.", indexed_documents=0)


@app.post("/upload", status_code=202) # 202 Accepted, لأن الفهرسة قد تستغرق وقتًا
async def upload_file(file: UploadFile = File(...), current_rag_system: RAGSystem = Depends(get_rag_system)):
    upload_dir = "uploads_for_processing"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        logger.info(f"File '{file.filename}' uploaded successfully to '{file_path}'.")

        return {
            "filename": file.filename,
            "message": (
                f"File '{file.filename}' uploaded to server. "
                "To include it in the RAG system, its content needs to be processed and "
                "added to the MySQL database, followed by a re-index operation via the /reindex endpoint."
            )
        }

    except Exception as e:
        logger.error(f"Error uploading file '{file.filename}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Could not upload or process file: {str(e)}")


if __name__ == "__main__":
    # الحصول على host و port من متغيرات البيئة أو استخدام القيم الافتراضية
    # لم نعد بحاجة لـ config_for_server = Config() هنا لهذا الغرض المحدد

    # استخدام os.getenv مباشرة هنا
    api_host = os.getenv("API_HOST", "127.0.0.1")
    api_port = int(os.getenv("API_PORT", "8080")) # Changed default port to 8080

    logger.info(f"Starting API server on http://{api_host}:{api_port}...")
    logger.info("Ensure your .env file is configured and MySQL database is accessible.")
    logger.info(f"Access API documentation at http://{api_host}:{api_port}/docs")

    uvicorn.run(
        "homework_helper.api_server:app", # المسار إلى كائن التطبيق
        host=api_host,
        port=api_port,
        log_level="info",
        reload=True # تفعيل إعادة التحميل التلقائي في وضع التطوير
    )
    # لتشغيل من جذر المشروع: python -m homework_helper.api_server
