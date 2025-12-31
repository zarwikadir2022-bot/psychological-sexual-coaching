import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. إعداد قاعدة البيانات ---
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

# --- 2. إعدادات الأمان (كلمة المرور) ---
# يمكنك تغيير كلمة المرور هنا بسهولة بين العلامتين " "
ADMIN_PASSWORD = "admin2026" 

# --- 3. فضاء العميل (واجهة الحجز) ---
def client_page():
    st.header("🌱 فضاء الحجز الآمن - استشارات تخصصية")
    st.write("نحن هنا للاستماع إليك في بيئة آمنة تضمن لك كامل السرية والخصوصية.")
    
    with st.form("consultation_form"):
        st.subheader("1. البيانات الأساسية")
        name = st.text_input("الاسم (أو اسم مستعار)")
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
        
        description = st.text_area("وصف موجز للحالة (اختياري)")
        
        st.subheader("3. تحديد الموعد")
        date = st.date_input("اليوم المفضل")
        time = st.time_input("التوقيت المقترح")
        
        submitted = st.form_submit_button("إرسال طلب الحجز")
        
        if submitted:
            if name:
                conn = sqlite3.connect('consultations_secure.db')
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, age, service, mood, description, date, time, timestamp) VALUES (?,?,?,?,?,?,?,?)",
                          (name, age, service, mood, description, str(date), str(time), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("✅ تم استلام طلبك بنجاح. سنقوم بالتواصل معك قريباً.")
                st.balloons()
            else:
                st.error("الرجاء إدخال الاسم لضمان المتابعة.")

    # سياسة الخصوصية
    st.markdown("---")
    with st.expander("⚖️ سياسة الخصوصية وحماية المعطيات الشخصية"):
        st.write("""
        - بياناتكم محمية بموجب السرية المهنية التامة.
        - نلتزم بالقانون التونسي عدد 63 لسنة 2004 المتعلق بحماية المعطيات الشخصية.
        - لا يتم مشاركة بياناتكم مع أي طرف ثالث.
        """)

# --- 4. لوحة تحكم المدير (Admin Dashboard) ---
def admin_page():
    st.sidebar.title("🔐 دخول الإدارة")
    password_input = st.sidebar.text_input("كلمة المرور", type="password")
    
    if password_input == ADMIN_PASSWORD:
        st.sidebar.success("تم الدخول بنجاح")
        st.title("📊 إدارة المواعيد وتحليل البيانات")
        
        conn = sqlite3.connect('consultations_secure.db')
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            # عرض مؤشرات سريعة (Analytics)
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الحجوزات", len(df))
            col2.metric("الحالات العاجلة", len(df[df['mood'] == 'سيئة جداً']))
            col3.metric("نوع الاستشارة الأكثر طلباً", df['service'].mode()[0])
            
            st.write("---")
            st.subheader("سجل الحجوزات التفصيلي")
            st.dataframe(df)
            
            # زر لتحميل البيانات كملف Excel للتحليل المتقدم
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل التقرير (CSV)", csv, "consultations.csv", "text/csv")
        else:
            st.info("لا توجد حجوزات مسجلة في قاعدة البيانات حتى الآن.")
    else:
        if password_input != "":
            st.sidebar.error("كلمة المرور غير صحيحة")
        st.warning("الرجاء إدخال كلمة المرور من القائمة الجانبية للوصول للبيانات.")

# --- 5. التشغيل الرئيسي ---
def main():
    st.set_page_config(page_title="منصة الاستشارات المتكاملة", page_icon="🌱")
    init_db()
    
    choice = st.sidebar.selectbox("القائمة", ["حجز استشارة", "لوحة التحكم"])
    
    if choice == "حجز استشارة":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
