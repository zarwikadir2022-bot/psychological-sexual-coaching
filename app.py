import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime

# --- 1. إعدادات الصفحة (يجب أن يكون أول أمر) ---
st.set_page_config(
    page_title="فضاء الاستشارة الذكي 2026",
    page_icon="🌿",
    layout="centered"
)

# --- 2. إعداد الذكاء الاصطناعي مع نظام كشف الأخطاء ---
def init_ai():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.warning("⚠️ تنبيه: لم يتم العثور على GOOGLE_API_KEY في إعدادات Secrets.")
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # استخدام المسار الكامل للموديل
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"❌ خطأ في إعداد المحرك: {e}")
        return None

model = init_ai()

# --- 3. إدارة قاعدة البيانات ---
DB_NAME = 'clinic_final_debug_v7.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, age INTEGER, service TEXT, 
                  mood TEXT, contact_method TEXT, contact_details TEXT,
                  date TEXT, time TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- 4. التنسيق الجمالي (CSS) ---
st.markdown("""
<style>
    .stButton>button { border-radius: 20px; background-color: #E69F87; color: white; width: 100%; }
    .main { background-color: #FDFCF8; }
    .trust-box { background-color: #F3F0E7; padding: 20px; border-radius: 15px; border-right: 5px solid #E69F87; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 5. وظيفة المساعد الذكي 'أنيس' مع إظهار الأخطاء ---
def ai_chatbot():
    st.markdown("---")
    st.subheader("🤖 المساعد الذكي 'أنيس'")
    
    if not model:
        st.info("الذكاء الاصطناعي غير مفعل حالياً. يرجى مراجعة إعدادات المفتاح.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("اسأل أنيس شيئاً..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                context = "أنت 'أنيس'، مساعد ذكي لعيادة استشارات في تونس. تحدث بلهجة تونسية مهذبة."
                full_query = f"{context}\nسؤال المستخدم: {prompt}"
                
                response = model.generate_content(full_query)
                
                if response and response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error("جوجل لم تعد أي نص. قد يكون المحتوى محظوراً أو هناك مشكلة في الفلترة.")
                    
            except Exception as e:
                # هذا السطر هو الأهم: سيظهر لك الخطأ الحقيقي باللون الأحمر
                st.error(f"🚨 خطأ تقني من محرك جوجل: {e}")
                st.info("ملاحظة: إذا كان الخطأ يحتوي على 'User location is not supported'، فهذا يعني أن الخدمة تحتاج تفعيل إضافي للموقع أو تغيير السيرفر.")

# --- 6. صفحة العميل ---
def client_page():
    st.title("🌿 فضاء الاستشارة والخصوصية")
    
    with st.form("main_form"):
        st.subheader("📅 حجز موعد جديد")
        col1, col2 = st.columns(2)
        with col1: name = st.text_input("الاسم")
        with col2: age = st.number_input("العمر", 18, 100, 25)
        
        details = st.text_input("رقم الهاتف أو الإيميل")
        service = st.selectbox("نوع الخدمة", ["توازن نفسي", "صحة جنسية", "كوتشينغ"])
        
        if st.form_submit_button("إرسال الطلب"):
            if name and details:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, age, service, contact_details, timestamp) VALUES (?,?,?,?,?)",
                          (name, age, service, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("تم الحجز!")
            else: st.error("أكمل البيانات")

    ai_chatbot()

# --- 7. التشغيل ---
def main():
    init_db()
    menu = st.sidebar.radio("التنقل", ["فضاء العميل", "لوحة التحكم"])
    if menu == "فضاء العميل":
        client_page()
    else:
        # لوحة التحكم البسيطة
        pwd = st.sidebar.text_input("رمز الإدارة", type="password")
        if pwd == "admin2026":
            st.title("📊 الإدارة")
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql_query("SELECT * FROM bookings", conn)
            conn.close()
            st.dataframe(df)

if __name__ == '__main__':
    main()
