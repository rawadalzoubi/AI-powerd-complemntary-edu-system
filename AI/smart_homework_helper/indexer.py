import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import Config
from pipelines.text_pipeline import TextPipeline
from pipelines.image_pipeline import ImagePipeline
# استيراد خط الفيديو الجديد
try:
    from pipelines.video_pipeline import VideoPipeline
except ImportError:
    print("Warning: VideoPipeline not found. Video features will be disabled.")
    VideoPipeline = None

# إعداد السجل (Logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SmartIndexerHandler(FileSystemEventHandler):
    """
    كلاس معالج الأحداث: يستجيب عند إنشاء ملف جديد (PDF أو فيديو)
    """
    def __init__(self):
        logger.info("--- Initializing Pipelines (Loading Models)... ---")
        
        self.text_pipe = TextPipeline(Config)
        self.image_pipe = ImagePipeline(Config)
        
        if VideoPipeline:
            self.video_pipe = VideoPipeline(Config)
        else:
            self.video_pipe = None
            
        logger.info("--- Pipelines Ready. Watching for new files... ---")

    def on_created(self, event):
        """
        يتم استدعاء هذه الدالة تلقائياً عند إنشاء ملف جديد.
        """
        if event.is_directory:
            return
        
        filename = event.src_path
        # التحقق من الامتداد (PDF أو فيديو)
        is_pdf = filename.endswith('.pdf')
        is_video = filename.endswith(('.mp4', '.mkv', '.avi', '.mov'))

        if not (is_pdf or is_video):
            return

        logger.info(f"🆕 New file detected: {filename}")
        
        # انتظار قصير للتأكد من اكتمال نسخ الملف
        time.sleep(2)
        
        self.process_file(filename, is_pdf, is_video)

    def process_file(self, file_path, is_pdf, is_video):
        """
        تشغيل الفهرسة للملف الجديد
        """
        try:
            logger.info(f"⚡ Indexing started for: {os.path.basename(file_path)}")
            specific_file_list = [file_path]

            if is_pdf:
                # ملف PDF: نفهرس نصوصه وصوره
                logger.info("   > Processing PDF content (Text & Images)...")
                self.text_pipe.run(files_to_process=specific_file_list)
                self.image_pipe.run(files_to_process=specific_file_list)
            
            elif is_video and self.video_pipe:
                # ملف فيديو: نفهرس نصوصه (Audio -> Text)
                logger.info("   > Processing Video content (Audio Transcription)...")
                self.video_pipe.run(files_to_process=specific_file_list)
            
            logger.info(f"✅ Successfully indexed: {os.path.basename(file_path)}")
            
        except Exception as e:
            logger.error(f"❌ Error indexing file {file_path}: {e}")

def run_watcher():
    """
    الدالة الرئيسية لتشغيل المراقبة (أو الفهرسة الأولية)
    """
    if not os.path.exists(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)
        logger.info(f"Created data directory: {Config.DATA_DIR}")

    # 1. الفهرسة الأولية (Initial Indexing) للملفات الموجودة
    logger.info("--- Running Initial Indexing for existing files... ---")
    
    # PDF Files
    pdf_files = [os.path.join(Config.DATA_DIR, f) for f in os.listdir(Config.DATA_DIR) if f.endswith('.pdf')]
    if pdf_files:
        logger.info(f"Found {len(pdf_files)} PDFs. Processing...")
        text_pipe = TextPipeline(Config)
        image_pipe = ImagePipeline(Config)
        text_pipe.run(files_to_process=pdf_files)
        image_pipe.run(files_to_process=pdf_files)
    
    # Video Files
    if VideoPipeline:
        video_files = [os.path.join(Config.DATA_DIR, f) for f in os.listdir(Config.DATA_DIR) if f.endswith(('.mp4', '.mkv', '.avi'))]
        if video_files:
            logger.info(f"Found {len(video_files)} Videos. Processing...")
            video_pipe = VideoPipeline(Config)
            video_pipe.run(files_to_process=video_files)

    logger.info("--- Initial Indexing Complete. Starting Watcher... ---")

    # 2. تشغيل المراقب (Watcher)
    event_handler = SmartIndexerHandler()
    observer = Observer()
    observer.schedule(event_handler, Config.DATA_DIR, recursive=False)
    observer.start()
    
    logger.info(f"👀 WATCHER IS RUNNING... Drop PDFs or Videos into '{Config.DATA_DIR}'")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("🛑 Watcher stopped by user.")
    
    observer.join()

if __name__ == "__main__":
    run_watcher()