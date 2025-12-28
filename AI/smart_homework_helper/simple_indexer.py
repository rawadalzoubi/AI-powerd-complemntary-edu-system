"""
Simple Indexer - فهرسة بسيطة بدون watchdog
"""
import os
import sys

# إضافة المسار للـ imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from pipelines.text_pipeline import TextPipeline
from pipelines.image_pipeline import ImagePipeline

def main():
    print("=" * 50)
    print("🚀 Starting Simple Indexer")
    print("=" * 50)
    
    # التأكد من وجود مجلد البيانات
    if not os.path.exists(Config.DATA_DIR):
        print(f"❌ Data directory not found: {Config.DATA_DIR}")
        print("   Please create the directory and add your PDF files.")
        return
    
    # عرض الملفات الموجودة
    files = os.listdir(Config.DATA_DIR)
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    print(f"\n📁 Found {len(pdf_files)} PDF files in {Config.DATA_DIR}")
    for f in pdf_files:
        print(f"   - {f}")
    
    if not pdf_files:
        print("❌ No PDF files found!")
        return
    
    # 1. فهرسة النصوص
    print("\n" + "=" * 50)
    print("📝 Step 1: Indexing Text Content (with OCR)")
    print("=" * 50)
    
    text_pipeline = TextPipeline(Config)
    text_pipeline.run()
    
    # 2. فهرسة الصور
    print("\n" + "=" * 50)
    print("🖼️ Step 2: Indexing Images")
    print("=" * 50)
    
    image_pipeline = ImagePipeline(Config)
    image_pipeline.run()
    
    print("\n" + "=" * 50)
    print("✅ Indexing Complete!")
    print("=" * 50)
    print("\nYou can now run: python api.py")

if __name__ == "__main__":
    main()
