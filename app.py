import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="فضاء الاستشارة الذكي 2026",
    page_icon="🌿",
    layout="centered"
)

# --- 2. إعداد الذكاء الاصطناعي (تم تعديل اسم الموديل لحل خطأ 404) ---
def init_ai():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # حذفنا 'models/' واستخدمنا الاسم المباشر الذي تقبله نسخة v1beta
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"خطأ في الإعداد: {e}")
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
        st.subheader("📅 حجز موعد")
        name = st.text_input("الاسم")
        service = st.selectbox("الخدمة", ["نفسية", "جنسية", "زوجية", "كوتشينغ"])
        contact = st.text_input("الهاتف أو الإيميل")
        if st.form_submit_button("إرسال"):
            if name and contact:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, service, contact, timestamp) VALUES (?,?,?,?)",
                          (name, service, contact, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("تم الحجز!")
            else: st.error("أكمل البيانات")

    # الشات بوت (أنيس)
    if model:
        st.markdown("---")
        st.subheader("🤖 مساعدك الذكي 'أنيس'")
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        if prompt := st.chat_input("اسأل أنيس..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    # إضافة سياق لضمان رد مهني
                    response = model.generate_content(f"أجب كخبير استشارات في تونس بلهجة مهذبة: {prompt}")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"عذراً، أنيس يواجه صعوبة تقنية: {e}")

# --- 5. التشغيل ---
def main():
    init_db()
    menu = st.sidebar.radio("التنقل", ["فضاء العميل", "لوحة التحكم"])
    if menu == "فضاء العميل": client_page()
    else:
        pwd = st.sidebar.text_input("رمز الدخول", type="password")
        if pwd == "admin2026":
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query("SELECT * FROM bookings", conn)
            conn.close()
            st.dataframe(df)

if __name__ == '__main__':
    main()
