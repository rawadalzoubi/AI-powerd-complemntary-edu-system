import os
import base64
from io import BytesIO
from openai import OpenAI
import time

class AICorrector:
    def __init__(self, api_key=None):
        # إعداد الاتصال بـ OpenRouter
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            print("⚠️ [AICorrector] Warning: OPENROUTER_API_KEY not found.")
            self.client = None
        else:
            try:
                self.client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                )
                print("✅ [AICorrector] Connected to OpenRouter successfully.")
            except Exception as e:
                print(f"❌ [AICorrector] Error initializing OpenRouter client: {e}")
                self.client = None

        # --- إعدادات الموديلات ---
        # 1. مودل الرؤية (VLM)
        self.vlm_model_name = "qwen/qwen-2-vl-7b-instruct:free" # تأكد من الاسم الدقيق على OpenRouter
        # أو النسخة المدفوعة الرخيصة: "qwen/qwen-2-vl-7b-instruct"

        # 2. مودل التصحيح (Text Correction)
        # نستخدم Llama 3.2 3B لأنه صغير وسريع ومجاني غالباً
        self.correction_model_name = "meta-llama/llama-3.2-3b-instruct:free" 

    def _encode_image(self, pil_image):
        """تحويل صورة PIL إلى Base64"""
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def extract_text_from_image(self, pil_image):
        """
        استخدام Qwen2-VL عبر OpenRouter لاستخراج النص
        """
        if not self.client: return None
        
        try:
            # تحويل الصورة لـ Base64
            base64_image = self._encode_image(pil_image)
            
            prompt = """
            Extract all text from this image precisely.
            - If there are tables, output them in Markdown format.
            - Maintain Arabic characters correctly.
            - Ignore headers/footers if irrelevant.
            - Output ONLY the extracted text.
            """

            response = self.client.chat.completions.create(
                model=self.vlm_model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                # Qwen-VL قد يحتاج لضبط التوكنز
                max_tokens=2000, 
                temperature=0.1 # تقليل الإبداع لزيادة الدقة في النقل
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ [AICorrector] Qwen-VL Extraction Error: {e}")
            return None

    def correct_text(self, text):
        """
        استخدام Llama 3.2 (Small Model) لتصحيح النص
        """
        if not self.client or len(text) < 3: return text

        prompt = f"""
        Correct the spelling and grammatical errors in the following text (Arabic/English).
        - The text might come from ASR (Whisper) or OCR.
        - Fix common typos (e.g., Hamza, Ta-Marbuta).
        - Keep the scientific terms and meaning unchanged.
        - Output ONLY the corrected text.

        Text to correct:
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.correction_model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that corrects text errors only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ [AICorrector] Correction failed: {e}")
            return text