import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from PIL import Image

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="فضاء الاستشارات الآمن",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- لمسة CSS للألوان والجمالية ---
st.markdown("""
<style>
    .stButton>button {
        border-radius: 20px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    .stAlert {
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. إعداد قاعدة البيانات المحدثة ---
def init_db():
    conn = sqlite3.connect('consultations_secure.db')
    c = conn.cursor()
    # إضافة أعمدة وسيلة التواصل
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, age INTEGER, service TEXT, 
                  mood TEXT, description TEXT, 
                  contact_method TEXT, contact_details TEXT,
                  date TEXT, time TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- 2. إعدادات الأمان ---
ADMIN_PASSWORD = "admin2026" 

# --- 3. فضاء العميل ---
def client_page():
    try:
        image = Image.open('welcome_img.svg') 
        st.image(image, use_column_width=True)
    except:
        st.write("") 

    st.title("🌿 فضاءك الآمن للاستشارة")
    st.markdown("""
    <h4 style='text-align: center; color: #6B6B6B; font-weight: normal;'>
    نحن هنا لنستمع إليك بخصوصية تامة. اختر وسيلة التواصل التي تفضلها لنتمكن من الوصول إليك.
    </h4>
    """, unsafe_allow_html=True)
    st.write("---")
    
    with st.form("consultation_form"):
        st.subheader("📝 معلوماتك الأساسية")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم أو اللقب المستعار")
        with col2:
            age = st.number_input("العمر", min_value=18, max_value=90, step=1)
        
        st.subheader("📞 وسيلة التواصل المفضلة")
        contact_method = st.radio(
            "كيف تفضل أن نتواصل معك لتأكيد الموعد؟",
            ["الهاتف (WhatsApp/اتصال)", "البريد الإلكتروني (Email)"],
            horizontal=True
        )
        contact_details = st.text_input("أدخل رقم الهاتف أو الإيميل الخاص بك")

        st.subheader("💬 تفاصيل الجلسة")
        service = st.selectbox("نوع الاستشارة المطلوبة", [
            "🧠 استشارة نفسية (قلق، ضغوط، اكتئاب)",
            "❤️ استشارة في الصحة الجنسية والعلاقات",
            "🤝 استشارة زوجية وأسرية",
            "🚀 كوتشينغ أداء وتطوير ذاتي"
        ])
        
        mood = st.select_slider("كيف تشعر اليوم بشكل عام؟", 
                               options=["مرهق جداً", "منخفض الطاقة", "متوسط", "جيد", "ممتاز ومرتاح"], value="متوسط")
        
        description = st.text_area("مساحة حرة: صف لنا باختصار ما ترغب في مناقشته")
        
        st.subheader("📅 الموعد المفضل")
        col3, col4 = st.columns(2)
        with col3:
            date = st.date_input("اليوم المفضل")
        with col4:
            time = st.time_input("التوقيت المقترح")
        
        st.write("") 
        submitted = st.form_submit_button("تأكيد حجز الجلسة الآن", type="primary")
        
        if submitted:
            if name and contact_details:
                conn = sqlite3.connect('consultations_secure.db')
                c = conn.cursor()
                c.execute("""INSERT INTO bookings 
                          (name, age, service, mood, description, contact_method, contact_details, date, time, timestamp) 
                          VALUES (?,?,?,?,?,?,?,?,?,?)""",
                          (name, age, service, mood, description, contact_method, contact_details, str(date), str(time), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                
                st.success(f"✅ شكراً {name}. تم استلام طلبك، سنتواصل معك عبر {contact_method} في أقرب وقت.")
                st.balloons()
            else:
                st.warning("⚠️ يرجى إدخال الاسم ووسيلة التواصل لنتمكن من الرد عليك.")

    st.write("")
    with st.expander("🛡️ التزامنا بالخصوصية والسرية"):
        st.markdown("<div style='background-color: #F3F0E7; padding: 15px; border-radius: 10px;'>نلتزم بحماية بياناتك وسرية تواصلنا وفق القوانين المعمول بها.</div>", unsafe_allow_html=True)

# --- 4. لوحة تحكم المدير ---
def admin_page():
    st.sidebar.title("🔐 منطقة الإدارة")
    password_input = st.sidebar.text_input("كلمة المرور", type="password")
    
    if password_input == ADMIN_PASSWORD:
        st.title("📊 لوحة المتابعة")
        
        conn = sqlite3.connect('consultations_secure.db')
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            st.subheader("📋 قائمة الحجوزات ووسائل التواصل")
            # تلوين الجدول لسهولة القراءة
            st.dataframe(df)
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تصدير البيانات", csv, "consultations_full_report.csv", "text/csv")
        else:
            st.info("لا توجد طلبات جديدة.")
            
    elif password_input != "":
        st.sidebar.error("⛔ كلمة المرور خاطئة.")

# --- 5. التشغيل الرئيسي ---
def main():
    init_db()
    choice = st.sidebar.radio("التنقل", ["صفحة العميل (الحجز)", "لوحة التحكم (للإدارة)"])
    
    if choice == "صفحة العميل (الحجز)":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
