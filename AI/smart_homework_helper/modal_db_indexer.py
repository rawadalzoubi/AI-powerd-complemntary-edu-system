"""
Modal Cloud Indexer - بناء الفهرس من قاعدة البيانات MySQL على السحابة
يستخدم GPU للمعالجة السريعة ويدعم OCR
"""
import modal
import os
import time
import shutil
from dotenv import load_dotenv

load_dotenv()

# 1. تعريف الصورة (مع إضافة MySQL و Tesseract OCR)
image = (
    modal.Image.from_registry("nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04", add_python="3.10")
    .apt_install(
        "git", 
        "ffmpeg", 
        "libgl1-mesa-glx", 
        "tesseract-ocr", 
        "tesseract-ocr-ara", 
        "tesseract-ocr-eng",
        "default-libmysqlclient-dev",  # مكتبات MySQL
        "pkg-config"
    )
    .pip_install(
        "langchain",
        "langchain-community",
        "langchain-huggingface",
        "langchain-openai",
        "faiss-cpu",
        "pypdf",
        "pymupdf",
        "sentence-transformers",
        "python-dotenv",
        "python-pptx",
        "docx2txt",
        "Pillow",
        "pytesseract",
        "mysql-connector-python",  # للاتصال بـ MySQL
        "huggingface_hub"
    )
    .add_local_file("config.py", remote_path="/root/smart_homework_helper/config.py")
    .add_local_dir("filters", remote_path="/root/smart_homework_helper/filters")
    .add_local_dir("pipelines", remote_path="/root/smart_homework_helper/pipelines")
)

app = modal.App("homework-helper-db-indexer")

@app.function(
    image=image,
    gpu="T4",
    timeout=3600,
    secrets=[
        modal.Secret.from_dict({
            "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY", ""),
            "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
            "HF_TOKEN": os.getenv("HUGGINGFACE_API_KEY", ""),
            # إعدادات قاعدة البيانات
            "MYSQL_HOST": os.getenv("MYSQL_HOST", "localhost"),
            "MYSQL_USER": os.getenv("MYSQL_USER", "rawad"),
            "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD", "1234"),
            "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE", "edu_system"),
            "MYSQL_PORT": os.getenv("MYSQL_PORT", "3306")
        })
    ]
)
def run_cloud_db_indexer():
    """
    تشغيل الفهرسة من قاعدة البيانات على السحابة
    """
    import sys
    sys.path.append("/root/smart_homework_helper")
    
    from config import Config
    
    # تحديث المسارات للسحابة
    Config.DATA_DIR = "/root/smart_homework_helper/data"
    Config.VECTOR_DB_PATH = "/root/smart_homework_helper/faiss_index_cloud"
    
    # إنشاء المجلدات
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    os.makedirs(Config.VECTOR_DB_PATH, exist_ok=True)
    
    from filters.mysql_loader import MySQLLoader
    from pipelines.text_pipeline import TextPipeline
    from pipelines.image_pipeline import ImagePipeline
    
    print("=" * 70)
    print("🚀 Starting Cloud Database Indexer on Modal GPU")
    print("=" * 70)
    start_time = time.time()
    
    # ========================================
    # المرحلة 1: تحميل البيانات من MySQL
    # ========================================
    print("\n📥 [Phase 1] Loading Data from MySQL Database...")
    try:
        loader = MySQLLoader()
        documents = loader.load_data()
        
        if not documents:
            print("⚠️ No documents found in database!")
            return None
        
        print(f"✅ Loaded {len(documents)} documents from database")
        
        # إحصائيات
        lesson_docs = [d for d in documents if d.metadata.get('type') == 'lesson']
        qa_docs = [d for d in documents if d.metadata.get('type') == 'qa_explanation']
        
        print(f"   📚 Lesson content: {len(lesson_docs)}")
        print(f"   ❓ Q&A explanations: {len(qa_docs)}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Database Loading Error: {e}")
        return None
    
    # ========================================
    # المرحلة 2: بناء فهرس النصوص
    # ========================================
    print("\n📝 [Phase 2] Building Text Index (with OCR support)...")
    try:
        text_pipeline = TextPipeline(Config)
        text_pipeline.build_index_from_documents(documents)
        print("✅ Text indexing complete.")
        
        # عرض إحصائيات الفهرس
        if text_pipeline.vectorstore:
            total_vectors = text_pipeline.vectorstore.index.ntotal
            print(f"   📊 Total vectors in index: {total_vectors}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Text Pipeline Error: {e}")
        return None
    
    # ========================================
    # المرحلة 3: فهرسة الصور من PDFs (إن وجدت)
    # ========================================
    print("\n🖼️ [Phase 3] Image Indexing from PDFs...")
    try:
        # البحث عن ملفات PDF في data directory
        pdf_files = []
        if os.path.exists(Config.DATA_DIR):
            pdf_files = [
                os.path.join(Config.DATA_DIR, f) 
                for f in os.listdir(Config.DATA_DIR) 
                if f.endswith('.pdf')
            ]
        
        if pdf_files:
            print(f"   📄 Found {len(pdf_files)} PDF files")
            image_pipeline = ImagePipeline(Config)
            image_pipeline.run(files_to_process=pdf_files)
            print("✅ Image indexing complete.")
        else:
            print("   ℹ️ No PDF files found for image extraction")
            print("   💡 Tip: Upload PDFs to data/ folder for image indexing")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"⚠️ Image Pipeline Warning: {e}")
    
    # ========================================
    # المرحلة 4: التحقق من الفهرس
    # ========================================
    print("\n🔍 [Phase 4] Verifying Index...")
    try:
        test_pipeline = TextPipeline(Config)
        test_pipeline.load_index()
        
        if test_pipeline.vectorstore:
            # اختبار بحث بسيط
            test_query = "ما هو"
            results = test_pipeline.vectorstore.similarity_search(test_query, k=3)
            
            print(f"✅ Index verification successful")
            print(f"   📊 Total vectors: {test_pipeline.vectorstore.index.ntotal}")
            print(f"   🔍 Test search: Found {len(results)} results")
            
            if results:
                print("\n   📝 Sample results:")
                for i, doc in enumerate(results[:2], 1):
                    preview = doc.page_content[:80].replace('\n', ' ')
                    print(f"      {i}. {preview}...")
        else:
            print("⚠️ Index verification failed")
            return None
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Verification Error: {e}")
        return None
    
    end_time = time.time()
    print(f"\n✅ Indexing Complete in {end_time - start_time:.2f} seconds.")
    
    # ========================================
    # المرحلة 5: حزم النتائج للتنزيل
    # ========================================
    print("\n📦 [Phase 5] Packaging Results...")
    output_package = "/root/output_package"
    if os.path.exists(output_package):
        shutil.rmtree(output_package)
    os.makedirs(output_package)
    
    # نسخ الفهرس
    if os.path.exists(Config.VECTOR_DB_PATH):
        shutil.copytree(
            Config.VECTOR_DB_PATH, 
            os.path.join(output_package, "faiss_index")
        )
        print("   ✅ FAISS index packaged")
    
    # نسخ debug texts (إن وجدت)
    debug_texts_source = os.path.join(Config.DATA_DIR, "debug_extracted_texts")
    if os.path.exists(debug_texts_source):
        shutil.copytree(
            debug_texts_source, 
            os.path.join(output_package, "debug_texts")
        )
        print("   ✅ Debug texts packaged")
    
    # نسخ الصور المستخرجة (إن وجدت)
    extracted_images_source = os.path.join(Config.DATA_DIR, "extracted_images")
    if os.path.exists(extracted_images_source):
        shutil.copytree(
            extracted_images_source, 
            os.path.join(output_package, "extracted_images")
        )
        print("   ✅ Extracted images packaged")
    
    # إصلاح التوقيت (لتجنب مشاكل الضغط)
    current_time = time.time()
    for root, dirs, files in os.walk(output_package):
        for f in files:
            try:
                os.utime(os.path.join(root, f), (current_time, current_time))
            except:
                pass
        for d in dirs:
            try:
                os.utime(os.path.join(root, d), (current_time, current_time))
            except:
                pass
    
    # ضغط النتائج
    print("   🗜️ Compressing results...")
    shutil.make_archive("/root/final_output", 'zip', output_package)
    
    # قراءة الملف المضغوط
    with open("/root/final_output.zip", "rb") as f:
        zip_bytes = f.read()
    
    print(f"   📦 Package size: {len(zip_bytes) / (1024*1024):.2f} MB")
    
    return zip_bytes

@app.local_entrypoint()
def main():
    """
    نقطة الدخول المحلية - تشغيل الفهرسة وتنزيل النتائج
    """
    print("=" * 70)
    print("🌩️  Modal Cloud Database Indexer")
    print("=" * 70)
    print("\n📤 Triggering cloud indexer...")
    print("⏳ This may take several minutes depending on database size...\n")
    
    # تشغيل الفهرسة على السحابة
    zip_bytes = run_cloud_db_indexer.remote()
    
    if not zip_bytes:
        print("\n❌ Indexing failed! Check the logs above.")
        return
    
    print("\n📥 Downloading results...")
    with open("cloud_db_results.zip", "wb") as f:
        f.write(zip_bytes)
    
    print("📦 Extracting results...")
    
    # حذف المجلدات القديمة
    folders_to_clean = [
        "faiss_index",
        "text_index", 
        os.path.join("data", "debug_extracted_texts"),
        os.path.join("data", "extracted_images")
    ]
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"   🗑️ Cleaned old {folder}")
            except Exception as e:
                print(f"   ⚠️ Could not clean {folder}: {e}")
    
    # فك الضغط
    shutil.unpack_archive("cloud_db_results.zip", ".")
    
    # نقل الملفات للمواقع الصحيحة
    if os.path.exists("faiss_index"):
        print("   ✅ FAISS index extracted")
    
    if os.path.exists("debug_texts"):
        target = os.path.join("data", "debug_extracted_texts")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.exists(target):
            shutil.rmtree(target)
        shutil.move("debug_texts", target)
        print(f"   📄 Debug texts saved to: {target}")
    
    if os.path.exists("extracted_images"):
        target = os.path.join("data", "extracted_images")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.exists(target):
            shutil.rmtree(target)
        shutil.move("extracted_images", target)
        print(f"   🖼️ Extracted images saved to: {target}")
    
    print("\n" + "=" * 70)
    print("🎉 Cloud Database Indexing Complete!")
    print("=" * 70)
    print("\n📌 Next Steps:")
    print("   1. Start API: uvicorn api:app --reload")
    print("   2. Test: http://localhost:8000/docs")
    print("   3. Try a question!")
    print("\n")

if __name__ == "__main__":
    # يمكن تشغيله مباشرة
    print("💡 To run this script, use: modal run modal_db_indexer.py")
