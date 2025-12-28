import streamlit as st
import requests
from PIL import Image
import io

# عنوان الـ API (تأكد أن الخادم يعمل)
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="مساعد الواجبات الذكي", layout="wide", page_icon="🎓")

# --- تنسيق الصفحة ---
st.markdown("""
<style>
    .main { direction: rtl; font-family: 'Tajawal', sans-serif; }
    .stTextInput > div > div > input { text-align: right; }
    .stMarkdown { text-align: right; }
    div[data-testid="stImage"] { margin: auto; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 مساعد الواجبات الذكي (AI Tutor)")
st.caption("نظام تعليمي مدعوم بالذكاء الاصطناعي للإجابة على الأسئلة من المنهج الدراسي.")

# --- التبويبات ---
tab1, tab2, tab3 = st.tabs(["💬 محادثة نصية", "🖼️ بحث بالصور", "🎤 بحث صوتي"])

# === التبويب 1: المحادثة النصية ===
with tab1:
    st.header("اسأل المساعد")
    question = st.text_input("اكتب سؤالك هنا...", placeholder="مثال: ما هي نظرية فيثاغورث؟")
    
    if st.button("إرسال السؤال 🚀", key="btn_text"):
        if not question:
            st.warning("الرجاء كتابة سؤال أولاً.")
        else:
            with st.spinner("جاري التفكير..."):
                try:
                    response = requests.post(f"{API_URL}/answer", json={"question": question})
                    if response.status_code == 200:
                        data = response.json()
                        st.success("تم العثور على الإجابة!")
                        st.markdown(f"### الإجابة:\n{data['answer']}")
                        
                        # (مستقبلاً: عرض المصادر هنا)
                    else:
                        st.error(f"حدث خطأ: {response.text}")
                except Exception as e:
                    st.error(f"فشل الاتصال بالخادم: {e}")

# === التبويب 2: البحث بالصور ===
with tab2:
    st.header("ابحث باستخدام صورة")
    st.info("ارفع صورة لمخطط، رسم بياني، أو صفحة من الكتاب.")
    
    uploaded_file = st.file_uploader("اختر صورة...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        # عرض الصورة المرفوعة
        image = Image.open(uploaded_file)
        st.image(image, caption="الصورة المرفوعة", width=300)
        
        if st.button("بحث عن صور مشابهة 🔍", key="btn_img"):
            with st.spinner("جاري تحليل الصورة والبحث..."):
                try:
                    # إعادة ضبط المؤشر لقراءة الملف من البداية
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    
                    response = requests.post(f"{API_URL}/search-image", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        
                        if not results:
                            st.warning("لم يتم العثور على صور مشابهة.")
                        else:
                            st.success(f"وجدنا {len(results)} نتيجة مشابهة!")
                            
                            # عرض النتائج في أعمدة
                            cols = st.columns(len(results))
                            for idx, res in enumerate(results):
                                with cols[idx]:
                                    # محاولة عرض الصورة (يجب أن يكون المسار محلياً وصحيحاً)
                                    # ملاحظة: Streamlit يحتاج مساراً مطلقاً أو رابطاً
                                    # هنا سنعرض المعلومات فقط
                                    st.markdown(f"**المصدر:** {res['source']}")
                                    st.markdown(f"**الصفحة:** {res['page_number']}")
                                    with st.expander("النص المحيط"):
                                        st.write(res['context_text'])
                                    
                                    # لعرض الصورة، نحتاج لقراءتها من القرص
                                    if os.path.exists(res['image_path']):
                                        st.image(res['image_path'], caption=f"صفحة {res['page_number']}")
                                    else:
                                        st.warning("ملف الصورة غير موجود محلياً")
                    else:
                        st.error(f"خطأ في الخادم: {response.text}")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")

# === التبويب 3: البحث الصوتي ===
with tab3:
    st.header("تحدث مع المساعد")
    st.info("سجل سؤالك وسيقوم النظام بتحويله لنص والإجابة عليه.")
    
    audio_file = st.file_uploader("ارفع ملف صوتي (WAV, MP3, M4A)", type=["wav", "mp3", "m4a"])
    
    if audio_file is not None:
        st.audio(audio_file)
        
        if st.button("تحليل الصوت والإجابة 🎙️", key="btn_audio"):
            with st.spinner("جاري الاستماع والتحليل..."):
                try:
                    audio_file.seek(0)
                    files = {"file": (audio_file.name, audio_file, audio_file.type)}
                    
                    response = requests.post(f"{API_URL}/search-voice", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("تم الفهم!")
                        
                        st.markdown("### 📝 النص المستخرج:")
                        st.info(data['transcribed_text'])
                        
                        st.markdown("### 💡 الإجابة:")
                        st.markdown(data['answer'])
                    else:
                        st.error(f"خطأ في الخادم: {response.text}")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")

import os # تأكد من استيراد os في البداية