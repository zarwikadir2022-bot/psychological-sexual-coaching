import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. إعداد الصفحة (يجب أن يكون أول أمر إلزامي)
st.set_page_config(page_title="منصة الاستشارات 2026", page_icon="🌿", layout="centered")

# 2. إعداد قاعدة البيانات (باسم جديد تماماً)
DB_NAME = 'final_clinic_2026.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, age INTEGER, service TEXT, 
                  mood TEXT, description TEXT, 
                  contact_method TEXT, contact_details TEXT,
                  date TEXT, time TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# 3. الأمان
ADMIN_PASSWORD = "admin2026"

# 4. واجهة العميل
def client_page():
    st.title("🌿 فضاء الاستشارة والخصوصية")
    st.write("أهلاً بك. نحن هنا لنسمعك بكل أمان.")
    
    with st.form("main_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم أو اللقب المستعار")
        with col2:
            age = st.number_input("العمر", min_value=18, max_value=100, step=1)
        
        method = st.radio("وسيلة التواصل المفضلة", ["واتساب/هاتف", "إيميل"], horizontal=True)
        details = st.text_input("رقم الهاتف أو عنوان البريد الإلكتروني")
        
        service = st.selectbox("مجال الاستشارة", ["نفسية", "صحة جنسية", "علاقات زوجية", "كوتشينغ"])
        
        mood = st.select_slider("الحالة المزاجية الحالية", options=["سيئة", "متوسطة", "جيدة"])
        
        desc = st.text_area("رسالة إضافية (اختياري)")
        
        d = st.date_input("اليوم المطلوب")
        t = st.time_input("التوقيت المطلوب")
        
        if st.form_submit_button("إرسال الطلب"):
            if name and details:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, age, service, mood, description, contact_method, contact_details, date, time, timestamp) VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (name, age, service, mood, desc, method, details, str(d), str(t), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("تم الحجز بنجاح!")
            else:
                st.error("يرجى ملء الاسم ووسيلة التواصل.")

# 5. واجهة الإدارة
def admin_page():
    pwd = st.sidebar.text_input("كلمة المرور", type="password")
    if pwd == ADMIN_PASSWORD:
        st.title("📊 لوحة الإدارة")
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            st.metric("إجمالي الحجوزات", len(df))
            st.dataframe(df) # عرض بسيط بدون تعقيدات الألوان حالياً
            
            # رسم بياني بسيط مدمج (لا يحتاج matplotlib)
            st.subheader("توزيع الخدمات")
            st.bar_chart(df['service'].value_counts())
        else:
            st.info("لا توجد بيانات حالياً.")

# 6. التشغيل
def main():
    init_db()
    choice = st.sidebar.radio("التنقل", ["فضاء العميل", "لوحة التحكم"])
    if choice == "فضاء العميل":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
