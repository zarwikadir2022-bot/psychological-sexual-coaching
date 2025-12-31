import streamlit as st
import google.generativeai as genai

# دالة للتحقق من المفتاح وتفعيل الموديل
def setup_ai():
    # 1. التحقق من وجود المفتاح في Secrets
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("❌ المفتاح غير موجود! يرجى إضافته في إعدادات Secrets باسم GOOGLE_API_KEY")
        st.stop()
    
    # 2. جلب المفتاح
    api_key = st.secrets["GOOGLE_API_KEY"]
    
    # 3. إعداد الجوجل ذكاء اصطناعي
    try:
        genai.configure(api_key=api_key)
        # نستخدم موديل 1.5-flash لأنه الأسرع والأكثر توفيراً للرصيد المجاني
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"❌ فشل الاتصال بالمحرك الذكي: {e}")
        st.stop()

# استدعاء الدالة
model = setup_ai()
