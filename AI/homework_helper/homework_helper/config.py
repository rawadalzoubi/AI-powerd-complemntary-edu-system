import os
from dotenv import load_dotenv
import logging # إضافة استيراد logging

# Load environment variables from .env file
load_dotenv()
# إعداد Logger (إذا لم يتم إعداده بالفعل في main.py قبل استيراد هذا الملف)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'rawad'),
    'password': os.getenv('MYSQL_PASSWORD', '1234'),
    'database': os.getenv('MYSQL_DATABASE', 'edu_system'),
    'port': int(os.getenv('MYSQL_PORT', '3306'))
}

# Chunking Configuration
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
MAX_CHUNKS = int(os.getenv('MAX_CHUNKS', '50')) # Default to 50 for testing

# Retrieval Configuration
TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '5'))

# LLM Configuration
LLM_TYPE = os.getenv('LLM_TYPE', 'ollama').strip().lower()
OLLAMA_LLM_MODEL = os.getenv('OLLAMA_LLM_MODEL', 'mistral').strip()
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434').strip()
HUGGINGFACE_LLM_MODEL = os.getenv('HUGGINGFACE_LLM_MODEL', 'mistralai/Mistral-7B-Instruct-v0.1').strip()

# Embedder Configuration
EMBEDDER_TYPE = os.getenv('EMBEDDER_TYPE', 'huggingface').lower() # Default to huggingface
EMBEDDER_MODEL = os.getenv('EMBEDDER_MODEL', '').strip()

# HuggingFace API Key (for gated models or Hub interaction)
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '').strip()

# HuggingFace specific advanced settings (optional)
HUGGINGFACE_DEVICE = os.getenv('HUGGINGFACE_DEVICE', None) 
HUGGINGFACE_LLM_USE_SEQ2SEQ = os.getenv('HUGGINGFACE_LLM_USE_SEQ2SEQ', 'false').lower() == 'true'
HUGGINGFACE_LLM_TORCH_DTYPE_STR = os.getenv('HUGGINGFACE_LLM_TORCH_DTYPE', 'auto')
EMBEDDER_TRUST_REMOTE_CODE = os.getenv('EMBEDDER_TRUST_REMOTE_CODE', 'False').lower() == 'true'

# --- Replicate Configuration ---
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
REPLICATE_MODEL_IDENTIFIER = os.getenv('REPLICATE_MODEL_IDENTIFIER') # e.g., "owner/model-name:version-id"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo').strip()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '').strip()
DEEPSEEK_MODEL_NAME = os.getenv('DEEPSEEK_MODEL_NAME', 'deepseek-chat').strip()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '').strip()
OPENROUTER_MODEL_NAME = os.getenv('OPENROUTER_MODEL_NAME', 'openrouter-chat').strip()

SUPPORTED_LLM_TYPES = ['ollama', 'huggingface', 'replicate', 'openai', 'deepseek', 'openrouter']
SUPPORTED_EMBEDDER_TYPES = ['ollama', 'huggingface']

class Config:
    """Configuration class for the application."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        self.mysql_config = MYSQL_CONFIG
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP
        self.max_chunks = MAX_CHUNKS
        self.top_k_results = TOP_K_RESULTS
        
        self.llm_type = LLM_TYPE
        self.ollama_llm_model = OLLAMA_LLM_MODEL
        self.ollama_base_url = OLLAMA_BASE_URL
        self.huggingface_llm_model = HUGGINGFACE_LLM_MODEL
        
        # Determine the generic model name based on LLM_TYPE
        self.llm_model_name_for_type = None
        if self.llm_type == 'ollama':
            self.llm_model_name_for_type = self.ollama_llm_model
        elif self.llm_type == 'huggingface':
            self.llm_model_name_for_type = self.huggingface_llm_model
        # For 'replicate', the identifier is self.replicate_model_identifier, handled separately

        self.embedder_type = EMBEDDER_TYPE
        self.embedder_model = EMBEDDER_MODEL
        self.huggingface_api_key = HUGGINGFACE_API_KEY # هذا خاص بـ Hugging Face وليس OpenAI
        self.embedder_trust_remote_code = EMBEDDER_TRUST_REMOTE_CODE

        self.huggingface_device = HUGGINGFACE_DEVICE
        self.huggingface_llm_use_seq2seq = HUGGINGFACE_LLM_USE_SEQ2SEQ
        self.huggingface_llm_torch_dtype_str = HUGGINGFACE_LLM_TORCH_DTYPE_STR
        
        # Replicate Configuration
        self.replicate_api_token = REPLICATE_API_TOKEN
        self.replicate_model_identifier = REPLICATE_MODEL_IDENTIFIER

        # OpenAI Configuration
        self.openai_api_key = OPENAI_API_KEY
        self.openai_model_name = OPENAI_MODEL_NAME

        self.deepseek_api_key = DEEPSEEK_API_KEY
        self.deepseek_model_name = DEEPSEEK_MODEL_NAME
        self.openrouter_api_key = OPENROUTER_API_KEY
        self.openrouter_model_name = OPENROUTER_MODEL_NAME

    def validate(self):
        """Validate the configuration settings."""
        if not self.mysql_config['host']:
            raise ValueError("MySQL host is required")
        if not self.mysql_config['user']:
            raise ValueError("MySQL user is required")
        if not self.mysql_config['database']:
            raise ValueError("MySQL database name is required")
            
        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        if self.chunk_overlap < 0:
            raise ValueError("Chunk overlap must be non-negative")
        if self.max_chunks <= 0:
            raise ValueError("Max chunks must be positive")
        if self.top_k_results <= 0:
            raise ValueError("Top K results must be positive")
            
        # الآن القائمة المدعومة تقتصر على الخيارات المستخدمة فقط
        if self.llm_type not in SUPPORTED_LLM_TYPES:
            raise ValueError(f"LLM type '{self.llm_type}' is not supported. Supported types: {SUPPORTED_LLM_TYPES}")
        
        if self.llm_type == 'ollama':
            if not self.ollama_llm_model:
                raise ValueError("Ollama model name (OLLAMA_LLM_MODEL) is required when LLM_TYPE is 'ollama'")
            if not self.ollama_base_url:
                raise ValueError("Ollama base URL (OLLAMA_BASE_URL) is required when LLM_TYPE is 'ollama'")
        
        if self.llm_type == 'huggingface':
            if not self.huggingface_llm_model:
                raise ValueError("HuggingFace model name (HUGGINGFACE_LLM_MODEL) is required when LLM_TYPE is 'huggingface'")
            # يمكنك إضافة تحقق من self.huggingface_api_key هنا إذا كان النموذج يتطلبه دائمًا
            # ولكن الخطأ سيظهر عند محاولة تحميل النموذج إذا كان المفتاح مطلوبًا وغير موجود أو صالح

        if self.embedder_type not in SUPPORTED_EMBEDDER_TYPES:
            raise ValueError(f"Embedder type '{self.embedder_type}' must be either 'ollama' or 'huggingface'")

        if self.llm_type == "replicate":
            if not self.replicate_api_token:
                raise ValueError("REPLICATE_API_TOKEN must be set in .env file when LLM_TYPE is 'replicate'.")
            if not self.replicate_model_identifier:
                raise ValueError("REPLICATE_MODEL_IDENTIFIER must be set in .env file when LLM_TYPE is 'replicate'.")
            # Potentially validate the format of replicate_model_identifier if desired

        logger.info("Configuration validated successfully.") # تم التغيير إلى logger.info