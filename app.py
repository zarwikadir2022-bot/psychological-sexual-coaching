import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime

# --- 1. إعداد الصفحة (يجب أن يكون أول سطر برمي لـ streamlit) ---
st.set_page_config(page_title="منصة الاستشارات الذكية", page_icon="🌿", layout="centered")

# --- 2. إعداد الذكاء الاصطناعي بنظام الفحص الذاتي ---
def init_ai():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # البحث عن الموديل المتاح تلقائياً لتفادي خطأ 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # اختيار gemini-1.5-flash إذا وجد، وإلا اختيار أول موديل متاح
        target = 'models/gemini-1.5-flash'
        if target not in available_models:
            target = next((m for m in available_models if 'flash' in m), available_models[0])
            
        return genai.GenerativeModel(target)
    except Exception as e:
        # لا نعطل التطبيق، فقط نظهر تنبيهاً في الواجهة لاحقاً
        return f"Error: {e}"

# تشغيل الإعداد
model_or_error = init_ai()

# --- 3. قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('clinic_v2026.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, service TEXT, 
                  contact TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- 4. واجهة المستخدم ---
def main():
    init_db()
    st.title("🌿 فضاء الاستشارة والخصوصية")
    
    tab1, tab2 = st.tabs(["📅 حجز موعد", "🤖 استشارة ذكية"])

    with tab1:
        with st.form("booking"):
            name = st.text_input("الاسم")
            service = st.selectbox("الخدمة", ["نفسية", "جنسية", "زوجية", "كوتشينغ"])
            contact = st.text_input("رقم الهاتف أو الإيميل")
            if st.form_submit_button("تأكيد الحجز"):
                if name and contact:
                    conn = sqlite3.connect('clinic_v2026.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO bookings (name, service, contact, timestamp) VALUES (?,?,?,?)",
                              (name, service, contact, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    conn.close()
                    st.success("تم الحجز بنجاح!")
                else:
                    st.error("أكمل البيانات")

    with tab2:
        st.subheader("المساعد 'أنيس'")
        if isinstance(model_or_error, str):
            st.warning("🤖 أنيس في استراحة حالياً. يمكنك الحجز وسنتصل بك.")
            if st.sidebar.checkbox("أظهر تفاصيل الخطأ"):
                st.write(model_or_error)
        else:
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            if prompt := st.chat_input("اسأل أنيس..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.markdown(prompt)
                with st.chat_message("assistant"):
                    try:
                        response = model_or_error.generate_content(f"أجب بلهجة تونسية مهذبة: {prompt}")
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except:
                        st.write("عذراً، يرجى المحاولة لاحقاً.")

if __name__ == '__main__':
    main()
