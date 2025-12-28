import io
import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from rag_engine import rag_service

# --- نماذج البيانات (Pydantic Models) ---

class QueryRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str

# نموذج نتيجة البحث بالصور
class ImageResult(BaseModel):
    image_path: str
    source: str
    page_number: int  
    context_text: str
    confidence: Optional[str] = None  # مستوى الثقة

class ImageSearchResponse(BaseModel):
    results: List[ImageResult]

# نموذج نتيجة البحث الصوتي
class VoiceSearchResponse(BaseModel):
    transcribed_text: str
    answer: str

# --- إعداد التطبيق ---

app = FastAPI(title="Smart Homework Helper API (Multimodal)")

# إضافة CORS للسماح بالاتصال من Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    عند بدء التشغيل، نقوم بتحميل الفهارس الجاهزة من القرص.
    """
    rag_service.load_resources()

# --- نقاط النهاية (Endpoints) ---

@app.get("/")
def read_root():
    return {"status": "online", "message": "Homework Helper API is running. Use /docs to test."}

@app.post("/answer", response_model=AnswerResponse)
async def get_answer(request: QueryRequest):
    """
    نقطة النهاية للإجابة على الأسئلة النصية.
    """
    try:
        response_text = rag_service.answer_text_question(request.question)
        return AnswerResponse(answer=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-image", response_model=ImageSearchResponse)
async def search_image(file: UploadFile = File(...)):
    """
    نقطة النهاية للبحث بالصور.
    """
    try:
        # قراءة محتوى الملف
        contents = await file.read()
        image_stream = io.BytesIO(contents)
        
        # استدعاء دالة البحث في الصور من المنسق
        results_data = rag_service.search_image(image_stream)
        
        # إذا لم يتم العثور على نتائج
        if not results_data:
            return ImageSearchResponse(results=[{
                "image_path": "",
                "source": "لم يتم العثور على تطابق",
                "page_number": 0,
                "context_text": "لم أجد صورة مشابهة في الكتب المفهرسة. جرب إرسال صورة من المنهج الدراسي.",
                "confidence": None
            }])
        
        # تنظيف النتائج للتوافق مع النموذج
        clean_results = []
        for r in results_data:
            clean_results.append({
                "image_path": r.get("image_path", ""),
                "source": r.get("source", ""),
                "page_number": r.get("page_number", 0),
                "context_text": r.get("context_text", ""),
                "confidence": r.get("confidence", None)
            })
        
        return ImageSearchResponse(results=clean_results)
        
    except Exception as e:
        print(f"❌ ERROR processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Image Error: {str(e)}")

@app.post("/search-voice", response_model=VoiceSearchResponse)
async def search_voice(file: UploadFile = File(...)):
    """
    نقطة نهاية للبحث الصوتي: تستقبل ملف صوتي -> تحوله لنص -> تبحث عنه
    """
    import subprocess
    
    try:
        # حفظ الملف الصوتي مؤقتاً على القرص
        original_filename = f"temp_original_{file.filename}"
        converted_filename = "temp_audio.wav"
        
        with open(original_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check file size
        file_size = os.path.getsize(original_filename)
        print(f"📁 Received audio file: {file.filename}, size: {file_size} bytes")
        
        if file_size < 1000:  # Less than 1KB
            raise Exception("Audio file too small. Please record for longer.")
            
        try:
            # تحويل webm إلى wav باستخدام ffmpeg (إذا كان متاحاً)
            audio_file_to_use = original_filename
            
            if file.filename.endswith('.webm'):
                try:
                    # Try to convert webm to wav using ffmpeg
                    result = subprocess.run([
                        'ffmpeg', '-y', '-i', original_filename,
                        '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
                        converted_filename
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0 and os.path.exists(converted_filename):
                        audio_file_to_use = converted_filename
                        print(f"✅ Converted webm to wav successfully")
                    else:
                        print(f"⚠️ ffmpeg conversion failed, using original file")
                        print(f"ffmpeg stderr: {result.stderr}")
                except FileNotFoundError:
                    print("⚠️ ffmpeg not found, using original file")
                except Exception as conv_error:
                    print(f"⚠️ Conversion error: {conv_error}, using original file")
            
            # 1. تحويل الصوت إلى نص
            text_query = rag_service.transcribe_audio_file(audio_file_to_use)
            
            if not text_query or text_query.strip() == "":
                raise Exception("لم أتمكن من فهم الصوت. يرجى التحدث بوضوح والتسجيل لمدة أطول.")

            print(f"🎤 Transcribed Query: {text_query}")
            
            # 2. استخدام النص للبحث
            rag_response = rag_service.answer_text_question(text_query)
            
            return VoiceSearchResponse(
                transcribed_text=text_query,
                answer=rag_response
            )
            
        finally:
            # تنظيف: حذف الملفات المؤقتة
            for temp_file in [original_filename, converted_filename]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
    except Exception as e:
        print(f"❌ Voice Error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice Processing Error: {str(e)}")