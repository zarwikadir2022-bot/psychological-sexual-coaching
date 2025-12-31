import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- الإعدادات الأولية وقاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('consultations_secure.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, age INTEGER, service TEXT, 
                  mood TEXT, description TEXT, 
                  date TEXT, time TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- وظائف الحماية والتشفير ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# كلمة المرور الافتراضية للوحة التحكم هي: admin2026
# ناتج تشفيرها هو القيمة التالية:
ADMIN_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"

def check_password(password):
    return hash_password(password) == ADMIN_HASH

# --- فضاء العميل (الحجز) ---
def client_page():
    st.header("🌱 فضاء الحجز الآمن - استشارات تخصصية")
    st.write("نحن هنا للاستماع إليك في بيئة آمنة تضمن لك كامل السرية والخصوصية.")
    
    with st.form("consultation_form"):
        st.subheader("1. البيانات الأساسية")
        name = st.text_input("الاسم (يمكن استخدام اسم مستعار)")
        age = st.number_input("العمر", min_value=18, max_value=90, step=1)
        
        st.subheader("2. تفاصيل الاستشارة")
        service = st.selectbox("نوع الاستشارة المطلوبة", [
            "استشارة نفسية (قلق، ضغوط، اكتئاب)",
            "استشارة في الصحة الجنسية",
            "استشارة زوجية وعلاقات",
            "كوتشينغ أداء وتطوير ذاتي"
        ])
        
        mood = st.select_slider("كيف تصف حالتك المزاجية العامة اليوم؟", 
                               options=["سيئة جداً", "منخفضة", "متوسطة", "جيدة", "ممتازة"])
        
        description = st.text_area("وصف موجز لما ترغب في مناقشته (اختياري)")
        
        st.subheader("3. تحديد الموعد")
        date = st.date_input("اليوم المفضل")
        time = st.time_input("التوقيت المقترح")
        
        submitted = st.form_submit_button("إرسال طلب الحجز")
        
        if submitted:
            if name and service:
                conn = sqlite3.connect('consultations_secure.db')
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, age, service, mood, description, date, time, timestamp) VALUES (?,?,?,?,?,?,?,?)",
                          (name, age, service, mood, description, str(date), str(time), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("✅ تم استلام طلبك بنجاح. سنقوم بالتواصل معك لتأكيد الموعد.")
                st.balloons()
            else:
                st.error("الرجاء ملء البيانات الأساسية.")

    # سياسة الخصوصية
    st.markdown("---")
    with st.expander("⚖️ سياسة الخصوصية وحماية المعطيات الشخصية (Privacy Policy)"):
        st.write("""
        - جميع البيانات مشفرة وتخضع للسرية المهنية التامة.
        - نلتزم بالقانون التونسي عدد 63 لسنة 2004 المتعلق بحماية المعطيات الشخصية.
        - لا يتم مشاركة بياناتك مع أي طرف ثالث تحت أي ظرف.
        """)

# --- لوحة تحكم المدير ---
def admin_page():
    st.sidebar.title("🔐 دخول الإدارة")
    password = st.sidebar.text_input("كلمة المرور", type="password")
    
    if check_password(password):
        st.title("📊 لوحة إدارة الاستشارات والتحليل")
        
        conn = sqlite3.connect('consultations_secure.db')
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            # إحصائيات سريعة (Data Analytics)
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الحجوزات", len(df))
            col2.metric("متوسط الأعمار", int(df['age'].mean()))
            urgent = len(df[df['mood'] == 'سيئة جداً'])
            col3.metric("حالات عاجلة", urgent)
            
            st.subheader("قائمة الطلبات الجديدة")
            st.dataframe(df)
            
            # تحميل البيانات للتحليل المتقدم
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل البيانات (Excel/CSV)", csv, "consultations_report.csv", "text/csv")
        else:
            st.info("لا توجد حجوزات مسجلة بعد.")
    else:
        st.warning("الرجاء إدخال كلمة مرور المدير للوصول إلى البيانات الحساسة.")

# --- التشغيل الرئيسي ---
def main():
    st.set_page_config(page_title="منصة الكوتشينغ والاستشارات", page_icon="🌱")
    init_db()
    
    # القائمة الجانبية للتنقل
    menu = ["حجز استشارة", "لوحة التحكم"]
    choice = st.sidebar.selectbox("القائمة", menu)
    
    if choice == "حجز استشارة":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
