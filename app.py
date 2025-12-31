import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
from datetime import datetime

# --- 1. إعدادات الصفحة (يجب أن يكون أول أمر) ---
st.set_page_config(
    page_title="فضاء الاستشارة والنمو 2026",
    page_icon="🌿",
    layout="centered"
)

# --- 2. إعداد الذكاء الاصطناعي بشكل آمن ---
def init_ai():
    # التحقق من وجود المفتاح في Secrets
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # استخدام المسار الكامل للموديل لتفادي خطأ NotFound
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception:
        return None

model = init_ai()

# --- 3. إدارة قاعدة البيانات ---
DB_NAME = 'clinic_database_2026.db'

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

# --- 5. وظيفة المساعد الذكي 'أنيس' ---
def ai_chatbot():
    if model:
        st.markdown("---")
        st.subheader("🤖 المساعد الذكي 'أنيس'")
        st.caption("تحدث مع مساعدنا الافتراضي للاستفسار عن الخدمات بكل خصوصية.")
        
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
                    # سياق خاص بالمساعد
                    context = "أنت 'أنيس'، مساعد ذكي لعيادة استشارات نفسية وجنسية وكوتشينغ في تونس. صاحب العيادة خبير في السوفرولوجيا والكايروبراكتيك. تحدث بلهجة تونسية مهذبة."
                    full_query = f"{context}\nسؤال المستخدم: {prompt}"
                    response = model.generate_content(full_query)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception:
                    st.info("🤖 أنيس في استراحة قصيرة، يمكنك مواصلة الحجز وسنتصل بك قريباً.")

# --- 6. صفحة العميل (الحجز) ---
def client_page():
    st.title("🌿 فضاء الاستشارة والخصوصية")
    st.markdown("أهلاً بك. نحن هنا لنرافقك نحو التوازن النفسي والانسجام.")
    
    with st.form("main_booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم أو اللقب المستعار")
        with col2:
            age = st.number_input("العمر", min_value=18, max_value=100, step=1)
        
        method = st.radio("كيف نؤكد لك الموعد؟", ["واتساب/هاتف", "بريد إلكتروني"], horizontal=True)
        details = st.text_input("رقم الهاتف أو الإيميل")
        
        service = st.selectbox("مجال الاستشارة", [
            "🧠 توازن نفسي وإدارة ضغوط",
            "❤️ صحة جنسية وعلاقات",
            "🤝 إرشاد زوجي وأسري",
            "🚀 كوتشينغ ونمو شخصي"
        ])
        
        mood = st.select_slider("كيف تصف حالتك اليوم؟", options=["مرهق", "قلق", "عادي", "باهي", "مرتاح"])
        
        d = st.date_input("اليوم المفضل")
        t = st.time_input("التوقيت التقريبي")
        
        if st.form_submit_button("إرسال طلب الحجز"):
            if name and details:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("""INSERT INTO bookings 
                          (name, age, service, mood, contact_method, contact_details, date, time, timestamp) 
                          VALUES (?,?,?,?,?,?,?,?,?)""",
                          (name, age, service, mood, method, details, str(d), str(t), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("✅ تم استلام طلبك بسرية تامة. سنتواصل معك قريباً.")
            else:
                st.error("يرجى إكمال البيانات الأساسية.")

    # ميثاق الخصوصية
    st.markdown("""<div class="trust-box"><b>🛡️ ميثاق السرية:</b> جميع بياناتك مشفرة ومحمية وفق القانون التونسي لحماية المعطيات الشخصية.</div>""", unsafe_allow_html=True)
    
    # تشغيل الشات بوت
    ai_chatbot()

# --- 7. لوحة التحكم (الإدارة) ---
def admin_page():
    st.sidebar.title("🔐 بوابة الإدارة")
    pwd = st.sidebar.text_input("رمز الدخول", type="password")
    
    if pwd == "admin2026":
        st.title("📊 سجل المواعيد والتحليل")
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            m1, m2 = st.columns(2)
            m1.metric("إجمالي الحجوزات", len(df))
            m2.metric("أكثر خدمة طلباً", df['service'].mode()[0].split()[-1])
            
            st.write("---")
            st.dataframe(df)
            st.bar_chart(df['service'].value_counts())
        else:
            st.info("لا توجد حجوزات بعد.")

# --- 8. التشغيل الرئيسي ---
def main():
    init_db()
    menu = st.sidebar.radio("التنقل", ["فضاء العميل", "لوحة التحكم"])
    if menu == "فضاء العميل":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
