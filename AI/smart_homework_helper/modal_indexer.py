import modal
import os
import time
import shutil
import sys
from dotenv import load_dotenv

load_dotenv()

# === دمج ملفات الدروس من المنصة مع مجلد data ===
def prepare_data_folder():
    """
    نسخ ملفات الدروس من المنصة (media/lesson_files) إلى مجلد data
    قبل رفعها لـ Modal
    """
    # مسار ملفات الدروس في المنصة
    platform_files_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "..", 
        "backend", "Education", "Educational_system", "media", "lesson_files"
    )
    platform_files_path = os.path.abspath(platform_files_path)
    
    # مجلد data المحلي
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    # مجلد فرعي لملفات المنصة
    platform_data_dir = os.path.join(data_dir, "platform_lessons")
    
    if os.path.exists(platform_files_path):
        print(f"📂 Found platform files at: {platform_files_path}")
        
        # إنشاء مجلد platform_lessons إذا لم يكن موجوداً
        os.makedirs(platform_data_dir, exist_ok=True)
        
        # نسخ الملفات
        copied_count = 0
        for filename in os.listdir(platform_files_path):
            src = os.path.join(platform_files_path, filename)
            dst = os.path.join(platform_data_dir, filename)
            
            # نسخ فقط إذا الملف غير موجود أو تم تحديثه
            if os.path.isfile(src):
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                    shutil.copy2(src, dst)
                    copied_count += 1
                    print(f"   ✅ Copied: {filename}")
        
        print(f"📦 Total files copied from platform: {copied_count}")
    else:
        print(f"⚠️ Platform files not found at: {platform_files_path}")
    
    return data_dir

# تحضير الملفات قبل تعريف الصورة
prepare_data_folder()

# 1. تعريف الصورة (مع إضافة Tesseract OCR)
image = (
    modal.Image.from_registry("nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04", add_python="3.10")
    # --- التعديل هنا: إضافة tesseract ولغاته ---
    .apt_install("git", "ffmpeg", "libgl1-mesa-glx", "tesseract-ocr", "tesseract-ocr-ara", "tesseract-ocr-eng") 
    .pip_install(
        "langchain",
        "langchain-community",
        "langchain-huggingface",
        "langchain-openai",
        "faiss-cpu",
        "pypdf",
        "pymupdf",
        "sentence-transformers",
        "openai-whisper",
        "moviepy",
        "python-dotenv",
        "python-pptx",
        "docx2txt",
        "ultralytics",
        "opencv-python-headless",
        "huggingface_hub",
        "Pillow",
        "pytesseract" # مكتبة بايثون للتعامل مع OCR
    )
    .add_local_file("config.py", remote_path="/root/smart_homework_helper/config.py")
    .add_local_dir("filters", remote_path="/root/smart_homework_helper/filters")
    .add_local_dir("pipelines", remote_path="/root/smart_homework_helper/pipelines")
    .add_local_dir("utils", remote_path="/root/smart_homework_helper/utils")
    .add_local_dir("data", remote_path="/root/smart_homework_helper/data")  # يشمل الآن ملفات المنصة
)

app = modal.App("homework-helper-indexer")

@app.function(
    image=image,
    gpu="T4",
    timeout=3600,
    secrets=[modal.Secret.from_dict({
        "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY", ""),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
        "HF_TOKEN": os.getenv("HUGGINGFACE_API_KEY", "") 
    })]
)
def run_cloud_indexer():
    import sys
    sys.path.append("/root/smart_homework_helper")
    
    from config import Config
    Config.DATA_DIR = "/root/smart_homework_helper/data"
    Config.VECTOR_DB_PATH = "/root/smart_homework_helper/faiss_index_cloud"
    
    from pipelines.text_pipeline import TextPipeline
    from pipelines.image_pipeline import ImagePipeline
    
    # تعطيل الفيديو
    VideoPipeline = None

    print("🚀 Starting Indexer on Modal GPU (OCR Enabled)...")
    start_time = time.time()

    # 1. النصوص (الآن يدعم OCR)
    print("\n--- [Phase 1] Text Indexing (with OCR Fallback) ---")
    try:
        text_pipe = TextPipeline(Config)
        text_pipe.run()
        print("✅ Text indexing complete.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Text Pipeline Error: {e}")

    # 2. الصور
    print("\n--- [Phase 2] Image Indexing ---")
    try:
        image_pipe = ImagePipeline(Config)
        image_pipe.run()
        print("✅ Image indexing complete.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Image Pipeline Error: {e}")

    # 3. الفيديو (معطل)
    print("\n--- [Phase 3] Video Indexing (SKIPPED) ---")
    
    end_time = time.time()
    print(f"✅ Indexing Complete in {end_time - start_time:.2f} seconds.")

    # حزم النتائج
    import shutil
    output_package = "/root/output_package"
    if os.path.exists(output_package): shutil.rmtree(output_package)
    os.makedirs(output_package)
    
    if os.path.exists(Config.VECTOR_DB_PATH):
        shutil.copytree(Config.VECTOR_DB_PATH, os.path.join(output_package, "faiss_index"))
    
    debug_texts_source = os.path.join(Config.DATA_DIR, "debug_extracted_texts")
    if os.path.exists(debug_texts_source):
        shutil.copytree(debug_texts_source, os.path.join(output_package, "debug_texts"))

    extracted_images_source = os.path.join(Config.DATA_DIR, "extracted_images")
    if os.path.exists(extracted_images_source):
        shutil.copytree(extracted_images_source, os.path.join(output_package, "extracted_images"))

    # إصلاح التوقيت
    current_time = time.time()
    for root, dirs, files in os.walk(output_package):
        for f in files:
            try: os.utime(os.path.join(root, f), (current_time, current_time))
            except: pass
        for d in dirs:
            try: os.utime(os.path.join(root, d), (current_time, current_time))
            except: pass

    shutil.make_archive("/root/final_output", 'zip', output_package)
    
    with open("/root/final_output.zip", "rb") as f:
        return f.read()

@app.local_entrypoint()
def main():
    print("Triggering cloud indexer...")
    zip_bytes = run_cloud_indexer.remote()
    
    print("Downloading results...")
    with open("cloud_results.zip", "wb") as f:
        f.write(zip_bytes)
    
    print("Extracting results...")
    for folder in ["faiss_index", "data/debug_extracted_texts", "data/extracted_images"]:
        if os.path.exists(folder):
            try: shutil.rmtree(folder)
            except: pass
        
    shutil.unpack_archive("cloud_results.zip", ".")
    
    if os.path.exists("faiss_index_cloud"):
         os.rename("faiss_index_cloud", "faiss_index")
         
    if os.path.exists("debug_texts"):
        target = os.path.join("data", "debug_extracted_texts")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.move("debug_texts", target)
        print(f"📄 Text debug logs saved to: {target}")

    if os.path.exists("extracted_images"):
        target = os.path.join("data", "extracted_images")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.move("extracted_images", target)
        print(f"🖼️  Extracted images saved to: {target}")
            
    print("🎉 Done! Text (with OCR) & Images updated.")
