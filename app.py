import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="منصة الاستشارات الذكية", page_icon="🌿", layout="centered")

# --- 2. إعداد الذكاء الاصطناعي (نسخة 2026 المستقرة) ---
def init_ai():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        
        # إعدادات الأمان للسماح بالرد على الاستشارات (بدون حظر تقني)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # استخدام الموديل الأكثر استقراراً
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            safety_settings=safety_settings
        )
        return model
    except Exception as e:
        st.error(f"خطأ في إعداد المحرك: {e}")
        return None

model = init_ai()

# --- 3. قاعدة البيانات ---
DB_NAME = 'clinic_final_2026.db'
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, service TEXT, 
                  contact TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- 4. واجهة العميل ---
def client_page():
    st.title("🌿 فضاء الاستشارة والخصوصية")
    
    with st.form("booking_form"):
        st.subheader("📅 حجز موعد جديد")
        name = st.text_input("الاسم")
        service = st.selectbox("الخدمة", ["نفسية", "صحة جنسية", "علاقات زوجية", "كوتشينغ"])
        contact = st.text_input("وسيلة التواصل (هاتف/إيميل)")
        if st.form_submit_button("إرسال طلب الحجز"):
            if name and contact:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, service, contact, timestamp) VALUES (?,?,?,?)",
                          (name, service, contact, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("✅ تم الحجز بنجاح!")
            else: st.error("أكمل البيانات")

    # الشات بوت الذكي (أنيس)
    st.markdown("---")
    st.subheader("🤖 مساعدك الذكي 'أنيس'")
    
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("تحدث مع أنيس هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            if model:
                try:
                    # تعليمات النظام لضبط شخصية المساعد
                    instruction = "أنت مساعد ذكي لعيادة في تونس. اسمك أنيس. تحدث بلهجة تونسية مهذبة. قدم نصائح عامة وشجع على الحجز."
                    response = model.generate_content(f"{instruction} \n المستخدم: {prompt}")
                    
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"🚨 خطأ تقني: {e}")
            else:
                st.info("المساعد الذكي غير متاح حالياً، يرجى مواصلة الحجز.")

# --- 5. الإدارة والتشغيل ---
def admin_page():
    pwd = st.sidebar.text_input("رمز الدخول", type="password")
    if pwd == "admin2026":
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM bookings", conn)
        conn.close()
        st.dataframe(df)

def main():
    init_db()
    menu = st.sidebar.radio("التنقل", ["فضاء العميل", "لوحة التحكم"])
    if menu == "فضاء العميل": client_page()
    else: admin_page()

if __name__ == '__main__':
    main()
