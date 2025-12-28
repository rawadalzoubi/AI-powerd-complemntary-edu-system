import os
import logging
from dotenv import load_dotenv

# إعداد Logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

class Config:
    # مفاتيح API
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    
    # أسماء النماذج
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
    IMAGE_EMBEDDING_MODEL_NAME = os.getenv("IMAGE_EMBEDDING_MODEL", "clip-ViT-B-32")
    
    # --- الجديد: نموذج Re-ranker ---
    # نستخدم bge-reranker-base لأنه ممتاز للعربية والإنجليزية
    RERANKER_MODEL_NAME = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
    
    # إعدادات التقطيع والاسترجاع
    CHUNK_SIZE = 1000       
    CHUNK_OVERLAP = 200     
    
    # استراتيجية المرحلتين:
    # 1. نسترجع عدداً كبيراً بسرعة (Initial Retrieval)
    INITIAL_TOP_K = 10     
    # 2. نختار الأفضل بدقة بعد إعادة الترتيب (Final Context)
    FINAL_TOP_K = 3        
    TOP_K_RETRIEVAL = 10  # عدد النتائج التي يسترجعها من الفهرس

    # مسارات الملفات
    DATA_DIR = "./data"             
    VECTOR_DB_PATH = "./faiss_index"
    
    # إعدادات قاعدة البيانات MySQL
    mysql_config = {
        'host': os.getenv("MYSQL_HOST", "localhost"),
        'user': os.getenv("MYSQL_USER", "rawad"),
        'password': os.getenv("MYSQL_PASSWORD", "1234"),
        'database': os.getenv("MYSQL_DATABASE", "edu_system"),
        'port': int(os.getenv("MYSQL_PORT", "3306"))
    }