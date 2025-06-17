import logging
from typing import List, Dict, Any

# استيراد فئة Config لإدارة الإعدادات
from .config import Config

# استيراد جميع الفلاتر والمكونات من المسارات الصحيحة
from .filters.mysql_loader import MySQLLoader
from .filters.pdf_parser import PDFParser # يفترض أن pdf_parser.py في مجلد filters
from .filters.chunker import Chunker
from .filters.embedder import create_embedder
from .filters.vector_store import VectorStore # يفترض أن vector_store.py في مجلد filters
from .filters.llm_answer import create_llm_answer

# إعداد المُسجِّل (logger)
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO) # يتم تكوينه في main.py أو config.py عادةً

class RAGSystem:
    """Retrieval-Augmented Generation system for answering questions based on document context."""

    def __init__(self, config: Config = None):
        """
        Initialize the RAG system.
        Args:
            config (Config, optional): A Config object. If None, one will be created.
        """
        if config is None:
            logger.info("No config provided, creating a new Config instance.")
            self.config = Config()
            self.config.validate() # التحقق من صحة الإعدادات
        else:
            self.config = config

        logger.info("Initializing RAG system components...")

        # تهيئة مكونات التحميل والمعالجة
        self.mysql_loader = MySQLLoader(config=self.config.mysql_config)
        self.pdf_parser = PDFParser() # لا يحتاج لإعدادات في __init__ حسب الكود السابق
        self.chunker = Chunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
            # max_chunks يمكن إضافتها هنا إذا كانت في Config ومستخدمة في Chunker
        )

        # تهيئة منشئ المتجهات (Embedder)
        embedder_kwargs = {"model_name": self.config.embedder_model}
        if self.config.embedder_type == "ollama":
            embedder_kwargs["base_url"] = self.config.ollama_base_url
        elif self.config.embedder_type == "huggingface":
            if self.config.huggingface_device: # التأكد من أن هذا الحقل موجود في Config
                embedder_kwargs["device"] = self.config.huggingface_device
        logger.info(f"Creating embedder: type={self.config.embedder_type}, model={self.config.embedder_model}")
        self.embedder = create_embedder(self.config.embedder_type, **embedder_kwargs)

        # تهيئة نموذج اللغة الكبير (LLM)
        llm_kwargs = {}
        if self.config.llm_type == "ollama":
            llm_kwargs["model_name"] = self.config.ollama_llm_model
            llm_kwargs["base_url"] = self.config.ollama_base_url
        elif self.config.llm_type == "huggingface":
            llm_kwargs["model_name"] = self.config.huggingface_llm_model
            if self.config.huggingface_device: # التأكد من أن هذا الحقل موجود في Config
                llm_kwargs["device"] = self.config.huggingface_device
            if hasattr(self.config, 'huggingface_llm_use_seq2seq'):
                 llm_kwargs["use_seq2seq"] = self.config.huggingface_llm_use_seq2seq
            if hasattr(self.config, 'huggingface_llm_torch_dtype_str') and self.config.huggingface_llm_torch_dtype_str:
                 llm_kwargs["torch_dtype"] = self.config.huggingface_llm_torch_dtype_str
            if hasattr(self.config, 'huggingface_api_key') and self.config.huggingface_api_key:
                 llm_kwargs["huggingface_api_key"] = self.config.huggingface_api_key
        elif self.config.llm_type == "replicate":
            if hasattr(self.config, 'replicate_api_token') and self.config.replicate_api_token:
                llm_kwargs["replicate_api_token"] = self.config.replicate_api_token
            if hasattr(self.config, 'replicate_model_identifier') and self.config.replicate_model_identifier:
                llm_kwargs["replicate_model_identifier"] = self.config.replicate_model_identifier
        elif self.config.llm_type == "openai":
            if hasattr(self.config, 'openai_api_key') and self.config.openai_api_key:
                llm_kwargs["openai_api_key"] = self.config.openai_api_key
            if hasattr(self.config, 'openai_model_name') and self.config.openai_model_name:
                llm_kwargs["model_name"] = self.config.openai_model_name
        elif self.config.llm_type == "deepseek":
            if hasattr(self.config, 'deepseek_api_key') and self.config.deepseek_api_key:
                llm_kwargs["deepseek_api_key"] = self.config.deepseek_api_key
            if hasattr(self.config, 'deepseek_model_name') and self.config.deepseek_model_name:
                llm_kwargs["model_name"] = self.config.deepseek_model_name
        elif self.config.llm_type == "openrouter":
            if hasattr(self.config, 'openrouter_api_key') and self.config.openrouter_api_key:
                llm_kwargs["openrouter_api_key"] = self.config.openrouter_api_key
            if hasattr(self.config, 'openrouter_model_name') and self.config.openrouter_model_name:
                llm_kwargs["model_name"] = self.config.openrouter_model_name

        logger.info(f"Creating LLM: type={self.config.llm_type}, model_kwargs containing model: {llm_kwargs.get('model_name') or llm_kwargs.get('replicate_model_identifier')}")
        self.llm = create_llm_answer(self.config.llm_type, **llm_kwargs)

        # تهيئة مخزن المتجهات (Vector Store)
        self.vector_store = VectorStore()

        # بناء الفهرس عند التهيئة
        self._initialize_system()

    def _initialize_system(self):
        """Build document index by loading, parsing, chunking, embedding, and storing."""
        logger.info("Starting document indexing process...")
        try:
            # 1. تحميل المستندات من MySQL
            #    MySQLLoader.process(None) أو MySQLLoader.load_documents()
            #    يفترض أن MySQLLoader.process يتجاهل المدخلات إذا كانت None ويقوم بالتحميل
            documents_from_db = self.mysql_loader.process(None)
            if not documents_from_db:
                logger.warning("No documents loaded from MySQL. Index will be empty.")
                self.vector_store.process([]) # تهيئة فهرس فارغ
                return
            logger.info(f"Loaded {len(documents_from_db)} documents/records from MySQL.")

            # 2. تحليل المستندات (مثل استخلاص النص من PDF إذا لزم الأمر)
            #    PDFParser.process تتوقع قائمة من القواميس، كل قاموس به 'content' (بايتس لملف PDF)
            #    وتعيد قائمة قواميس كل منها به 'text'
            parsed_documents = self.pdf_parser.process(documents_from_db)
            if not parsed_documents:
                logger.warning("No documents after parsing PDF/text. Index will be empty.")
                self.vector_store.process([])
                return
            logger.info(f"Successfully parsed {len(parsed_documents)} documents.")

            # 3. تقسيم المستندات إلى أجزاء (chunks)
            #    Chunker.process تتوقع قائمة من القواميس (مستندات مع 'text')
            #    وتعيد قائمة مسطحة من الأجزاء (chunks)
            all_text_chunks = self.chunker.process(parsed_documents)
            if not all_text_chunks:
                logger.warning("No chunks created from documents. Index will be empty.")
                self.vector_store.process([])
                return
            logger.info(f"Created {len(all_text_chunks)} text chunks.")

            # 4. إنشاء المتجهات (embeddings) للأجزاء
            #    Embedder.process تتوقع قائمة من الأجزاء (chunks) وتضيف مفتاح 'embedding' لكل جزء
            chunks_with_embeddings = self.embedder.process(all_text_chunks)
            logger.info(f"Generated embeddings for {len(chunks_with_embeddings)} chunks.")

            # 5. بناء فهرس FAISS في VectorStore
            #    VectorStore.process تتوقع قائمة من الأجزاء (chunks) مع 'embedding'
            self.vector_store.process(chunks_with_embeddings) # هذه الدالة تبني الفهرس داخل الكائن
            logger.info("Document index built successfully.")

        except Exception as e:
            logger.error(f"Error during system initialization and indexing: {e}", exc_info=True)
            # يمكنك اختيار إثارة الخطأ أو تركه ليتم التعامل معه لاحقًا
            # raise # إذا أردت إيقاف إنشاء الكائن عند فشل الفهرسة

    def answer_question(self, question: str, k: int = -1) -> Dict[str, Any]:
        """Answer a question using RAG pipeline."""
        if k == -1: # استخدام القيمة من الإعدادات إذا لم يتم تمريرها
            k = self.config.top_k_results

        logger.info(f"Answering question: \"{question[:100]}...\" using top_k={k}")
        try:
            # 1. إنشاء متجه للسؤال
            #    بعض الـ embedders لديها generate_embedding، والبعض الآخر يستخدم process
            #    الـ BaseEmbedder.process هو الواجهة الموحدة التي تتوقع قائمة وتعيد قائمة
            #    لذا سنستخدمها للاتساق، أو يمكنك التحقق من وجود generate_embedding واستخدامه.
            question_dict = {"text": question, "id": "query"} # إضافة id ليكون متسقًا مع ما قد يتوقعه embedder.process
            embedded_question_list = self.embedder.process([question_dict])

            if not embedded_question_list or not embedded_question_list[0].get("embedding"):
                logger.error("Failed to generate embedding for the question.")
                return {"answer": "Sorry, I could not process the question embedding.", "sources": []}
            query_embedding = embedded_question_list[0]["embedding"]

            # 2. البحث عن الأجزاء (chunks) ذات الصلة
            relevant_chunks = self.vector_store.search(query_embedding, k=k)
            if not relevant_chunks:
                logger.info("No relevant chunks found for the question.")
                # يمكنك اختيار إرجاع رسالة مخصصة هنا أو ترك النموذج اللغوي ليقول أنه لا يوجد سياق كاف
                # return {"answer": "I could not find relevant information to answer your question.", "sources": []}


            # 3. توليد الإجابة باستخدام نموذج اللغة
            answer = self.llm.generate_answer(question, relevant_chunks)

            sources = [
                {
                    "file_name": c.get("file_name", "N/A"),
                    "doc_id": c.get("doc_id", "N/A"), # إضافة doc_id إذا كان متاحًا
                    "text_snippet": c.get("text","")[:200] + "..." if c.get("text") else ""
                }
                for c in relevant_chunks
            ]
            logger.info(f"Generated answer. Number of sources provided to LLM: {len(sources)}")
            return {"answer": answer, "sources": sources}

        except Exception as e:
            logger.error(f"Error answering question: {e}", exc_info=True)
            # في بيئة الإنتاج، قد ترغب في إرجاع رسالة خطأ أكثر عمومية للمستخدم
            return {"answer": "Sorry, an unexpected error occurred while answering your question.", "sources": []}
            # أو raise e إذا كنت تريد معالجة الخطأ في مستوى أعلى

    def re_index(self):
        """Clear and rebuild document index."""
        logger.info("Re-indexing requested. Clearing old vector store and rebuilding...")
        # لإعادة الفهرسة بشكل كامل، نعيد تهيئة VectorStore ونعيد بناء الفهرس
        self.vector_store = VectorStore() # إنشاء كائن جديد لمسح الفهرس القديم والبيانات
        self._initialize_system()
        logger.info("Re-indexing completed.")

# Example instantiation (يفترض أن هذا الكود سيُستخدم من مكان آخر يقوم بإنشاء كائن Config):
# if __name__ == '__main__':
#     # هذا الجزء للاختبار ويتطلب وجود ملف .env صحيح
#     # وضبط مسارات الاستيراد إذا تم تشغيله مباشرة من هنا
#     try:
#         config = Config()
#         config.validate()
#         rag_system = RAGSystem(config=config)
#         test_question = "ما هي عاصمة فرنسا؟"
#         # يمكنك إضافة مستندات إلى قاعدة بياناتك أولاً ليكون هناك ما يتم فهرسته
#         # ثم اختبار الإجابة
#         # response = rag_system.answer_question(test_question)
#         # print("Question:", test_question)
#         # print("Answer:", response["answer"])
#         # print("Sources:", response["sources"])

#         # مثال على إعادة الفهرسة
#         # rag_system.re_index()
#         logger.info("RAGSystem instance created for testing (actual answering not run here).")

#     except Exception as e:
#         logger.error(f"Error in RAGSystem example: {e}", exc_info=True)