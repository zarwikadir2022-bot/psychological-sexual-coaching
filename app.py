import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime

# --- 1. إعداد الصفحة والذكاء الاصطناعي ---
st.set_page_config(
    page_title="فضاء الاستشارة الذكي 2026",
    page_icon="🌿",
    layout="centered"
)

# --- نظام الأمان: جلب المفتاح من Secrets ---
try:
    # سيقوم التطبيق بالبحث عن المفتاح في إعدادات Streamlit المخفية
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("خطأ: لم يتم العثور على مفتاح الـ API. يرجى إضافته في إعدادات Secrets.")
    st.stop()

# --- 2. إعداد قاعدة البيانات ---
DB_NAME = 'clinic_smart_v6.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, service TEXT, contact TEXT, 
                  mood TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- 3. تصميم الواجهة (CSS) ---
st.markdown("""
<style>
    .stButton>button { border-radius: 20px; background-color: #E69F87; color: white; width: 100%; }
    .main { background-color: #FDFCF8; }
</style>
""", unsafe_allow_html=True)

# --- 4. وظيفة المساعد الذكي (أنيس) ---
def ai_chatbot():
    st.markdown("---")
    st.subheader("🤖 المساعد الذكي 'أنيس'")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("اسأل 'أنيس' هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            system_instruction = (
                "أنت 'أنيس'، مساعد افتراضي لعيادة كوتشينغ واستشارات نفسية وجنسية في تونس. "
                "تحدث بلهجة تونسية مهذبة وبسيطة. كن متعاطفاً وحافظ على السرية."
            )
            
            try:
                full_prompt = f"{system_instruction}\nسؤال المستخدم: {prompt}"
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error("يرجى التأكد من إعداد المفتاح بشكل صحيح.")

# --- 5. فضاء العميل ---
def client_page():
    st.title("🌿 فضاء الاستشارة والخصوصية")
    with st.form("booking_form"):
        st.subheader("📅 حجز موعد جديد")
        name = st.text_input("الاسم أو الكنية")
        contact = st.text_input("رقم الهاتف أو الإيميل")
        service = st.selectbox("نوع الاستشارة", ["توازن نفسي", "صحة جنسية", "إرشاد زوجي", "كوتشينغ"])
        mood = st.select_slider("كيف حالك اليوم؟", options=["تعبان", "قلق", "عادي", "باهي", "مرتاح"])
        
        if st.form_submit_button("إرسال طلب الحجز"):
            if name and contact:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, service, contact, mood, timestamp) VALUES (?,?,?,?,?)",
                          (name, service, contact, mood, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("✅ تم استلام طلبك بنجاح.")
            else:
                st.error("الرجاء ملء البيانات.")
    ai_chatbot()

# --- 6. لوحة التحكم ---
def admin_page():
    pwd = st.sidebar.text_input("رمز الإدارة", type="password")
    if pwd == "admin2026":
        st.title("📊 سجل المواعيد")
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM bookings", conn)
        conn.close()
        st.dataframe(df)
    elif pwd != "":
        st.sidebar.error("الرمز خطأ")

# --- 7. التشغيل ---
def main():
    init_db()
    menu = st.sidebar.radio("القائمة", ["فضاء العميل", "لوحة التحكم"])
    if menu == "فضاء العميل":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
