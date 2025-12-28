
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from pipelines.base_pipeline import BasePipeline

# استيراد المصحح
from utils.ai_corrector import AICorrector

# استيراد معالج الفيديو
try:
    from filters.video_processor import VideoProcessor
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(file), '..')))
    from filters.video_processor import VideoProcessor

class VideoPipeline(BasePipeline):
    def init(self, config):
        super().init(config)
        print(f"[VideoPipeline] Initializing...")
        self.embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
        print("[VideoPipeline] Loading Whisper Model...")
        self.video_processor = VideoProcessor(model_id="openai/whisper-small")
        self.index_path = os.path.join(config.VECTOR_DB_PATH, "text_index")
        
        # ===> إضافة جديدة <===
        self.ai_helper = AICorrector(api_key=getattr(config, 'GOOGLE_API_KEY', None))

    def run(self, files_to_process=None):
        video_docs = []
        
        if files_to_process:
            target_files = files_to_process
        else:
             if not os.path.exists(self.config.DATA_DIR): return
             # البحث في المجلد الرئيسي والمجلدات الفرعية
             target_files = []
             for root, dirs, files in os.walk(self.config.DATA_DIR):
                 for f in files:
                     if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav')):
                         target_files.append(os.path.join(root, f))

        if not target_files: return
        print(f"[VideoPipeline] Processing {len(target_files)} videos...")

        for video_path in target_files:
            try:
                print(f"  -> Transcribing {os.path.basename(video_path)}...")
                segments = self.video_processor.transcribe_video(video_path)
                
                if segments:
                    for seg in segments:
                        raw_text = seg['text']
                        start_time = seg['start']
                        
                        if len(raw_text) < 10: continue

                        # ===> تطبيق طبقة التصحيح هنا <===
                        final_text = raw_text
                        # نصحح الجمل ذات الطول المعقول فقط
                        if self.ai_helper.model and len(raw_text.split()) > 3:
                            final_text = self.ai_helper.correct_text(raw_text)
                            # print(f"     Fixed: {raw_text} -> {final_text}") # Uncomment for debug

                        doc = Document(
                            page_content=final_text, # نستخدم النص المصحح
                            metadata={
                                "source": os.path.basename(video_path),
                                "media_type": "video",
                                "start_time": start_time,
                                "timestamp_str": f"{int(start_time//60)}:{int(start_time%60):02d}"
                            }
                        )
                        video_docs.append(doc)
            except Exception as e:
                print(f"Error processing video {video_path}: {e}")

        if not video_docs: return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.config.CHUNK_SIZE, chunk_overlap=self.config.CHUNK_OVERLAP)
        splits = text_splitter.split_documents(video_docs)


# (نفس كود الفهرسة والحفظ الأصلي)
        print(f"[VideoPipeline] Indexing {len(splits)} segments...")
        if os.path.exists(self.index_path):
             try:
                 old = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
                 old.merge_from(FAISS.from_documents(splits, self.embeddings))
                 self.vectorstore = old
             except:
                 self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        else:
             self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        
        self.vectorstore.save_local(self.index_path)
        print(f"[VideoPipeline] Index updated.")