"""
بناء الفهرس من قاعدة البيانات MySQL مباشرة
"""
import os
import logging
from config import Config
from filters.mysql_loader import MySQLLoader
from pipelines.text_pipeline import TextPipeline
from pipelines.image_pipeline import ImagePipeline

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def build_index():
    """
    بناء الفهرس من قاعدة البيانات
    """
    print("=" * 70)
    print("🚀 بدء بناء الفهرس من قاعدة البيانات MySQL")
    print("=" * 70)
    
    # 1. تحميل البيانات من MySQL
    print("\n📥 المرحلة 1: تحميل البيانات من قاعدة البيانات...")
    try:
        loader = MySQLLoader()
        documents = loader.load_data()
        
        if not documents:
            print("⚠️ لم يتم العثور على أي مستندات في قاعدة البيانات!")
            print("\n💡 تأكد من:")
            print("   1. وجود بيانات في جدول eduapi_lessoncontent")
            print("   2. وجود بيانات في جدول eduapi_lesson")
            print("   3. صحة الاتصال بقاعدة البيانات")
            return False
            
        print(f"✅ تم تحميل {len(documents)} مستند من قاعدة البيانات")
        
        # عرض إحصائيات
        lesson_docs = [d for d in documents if d.metadata.get('type') == 'lesson']
        qa_docs = [d for d in documents if d.metadata.get('type') == 'qa_explanation']
        
        print(f"   📚 محتوى الدروس: {len(lesson_docs)}")
        print(f"   ❓ أسئلة وأجوبة: {len(qa_docs)}")
        
    except Exception as e:
        print(f"❌ خطأ في تحميل البيانات: {e}")
        return False
    
    # 2. بناء فهرس النصوص
    print("\n📝 المرحلة 2: بناء فهرس النصوص...")
    try:
        text_pipeline = TextPipeline(Config)
        
        # تمرير المستندات مباشرة للفهرسة
        text_pipeline.build_index_from_documents(documents)
        
        print("✅ تم بناء فهرس النصوص بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في بناء فهرس النصوص: {e}")
        logger.error(f"Text indexing error: {e}", exc_info=True)
        return False
    
    # 3. بناء فهرس الصور (إذا كانت هناك ملفات PDF)
    print("\n🖼️ المرحلة 3: بحث عن ملفات PDF لفهرسة الصور...")
    try:
        # البحث عن ملفات PDF في media
        media_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'backend', 'Education', 'Educational_system', 'media', 'lesson_content'
        )
        
        if os.path.exists(media_path):
            pdf_files = [
                os.path.join(media_path, f) 
                for f in os.listdir(media_path) 
                if f.endswith('.pdf')
            ]
            
            if pdf_files:
                print(f"   📄 تم العثور على {len(pdf_files)} ملف PDF")
                print("   🔄 جاري فهرسة الصور...")
                
                image_pipeline = ImagePipeline(Config)
                image_pipeline.run(files_to_process=pdf_files)
                
                print("✅ تم بناء فهرس الصور بنجاح")
            else:
                print("   ℹ️ لم يتم العثور على ملفات PDF")
        else:
            print(f"   ⚠️ المسار غير موجود: {media_path}")
            
    except Exception as e:
        print(f"⚠️ تحذير: خطأ في فهرسة الصور: {e}")
        logger.warning(f"Image indexing warning: {e}")
    
    # 4. التحقق من الفهرس
    print("\n🔍 المرحلة 4: التحقق من الفهرس...")
    try:
        # إعادة تحميل الفهرس للتحقق
        test_pipeline = TextPipeline(Config)
        test_pipeline.load_index()
        
        if test_pipeline.vectorstore:
            # اختبار بحث بسيط
            test_query = "ما هو"
            results = test_pipeline.vectorstore.similarity_search(test_query, k=3)
            
            print(f"✅ الفهرس يعمل بشكل صحيح")
            print(f"   📊 عدد المتجهات: {test_pipeline.vectorstore.index.ntotal}")
            print(f"   🔍 اختبار بحث: تم العثور على {len(results)} نتيجة")
            
            if results:
                print("\n   📝 عينة من النتائج:")
                for i, doc in enumerate(results[:2], 1):
                    preview = doc.page_content[:100].replace('\n', ' ')
                    print(f"      {i}. {preview}...")
        else:
            print("⚠️ لم يتم تحميل الفهرس بشكل صحيح")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في التحقق من الفهرس: {e}")
        logger.error(f"Verification error: {e}", exc_info=True)
        return False
    
    print("\n" + "=" * 70)
    print("🎉 تم بناء الفهرس بنجاح!")
    print("=" * 70)
    print("\n📌 الخطوات التالية:")
    print("   1. تشغيل API: uvicorn api:app --reload")
    print("   2. اختبار النظام: http://localhost:8000/docs")
    print("   3. إرسال سؤال تجريبي")
    print("\n")
    
    return True

if __name__ == "__main__":
    success = build_index()
    exit(0 if success else 1)
