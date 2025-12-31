import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from PIL import Image

# --- إعدادات الصفحة والهوية البصرية ---
st.set_page_config(
    page_title="فضاء الاستشارات والنمو",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- لمسة جمالية CSS (ألوان دافئة ومحايدة) ---
st.markdown("""
<style>
    .stButton>button {
        border-radius: 20px;
        background-color: #E69F87;
        color: white;
        border: none;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 1px solid #F3F0E7;
    }
    .main {
        background-color: #FDFCF8;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. إدارة قاعدة البيانات (مع معالجة الأخطاء السابقة) ---
def init_db():
    # سنستخدم اسم ملف جديد لضمان تطبيق الهيكل الجديد فوراً
    conn = sqlite3.connect('consultations_v3.db')
    c = conn.cursor()
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

# --- 3. فضاء العميل (واجهة الاستقبال) ---
def client_page():
    # محاولة عرض صورة ترحيبية هادئة
    try:
        image = Image.open('welcome_img.png') 
        st.image(image, use_column_width=True)
    except:
        st.write("🌿")

    st.title("مرحباً بك في فضائك الخاص")
    st.markdown("<p style='color: #6B6B6B;'>نحن نؤمن بأن الصدق مع الذات هو أول خطوة نحو التحرر. اختر وسيلة التواصل التي تريحك، وسنكون بجانبك.</p>", unsafe_allow_html=True)
    
    with st.form("professional_booking_form"):
        st.subheader("📌 المعلومات الأساسية")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم (أو كنية تفضلها)")
        with col2:
            age = st.number_input("العمر", min_value=18, max_value=100, step=1)
        
        st.subheader("📞 كيف نصل إليك؟")
        contact_method = st.radio(
            "ما هي الوسيلة التي تفضلها للتواصل الأولي؟",
            ["واتساب / هاتف", "بريد إلكتروني"],
            horizontal=True
        )
        contact_details = st.text_input("أدخل الرقم أو الإيميل هنا")

        st.subheader("🔍 تفاصيل الاستشارة")
        service = st.selectbox("مجال الاستشارة", [
            "🧠 التوازن النفسي وإدارة الضغوط",
            "❤️ الصحة الجنسية والعلاقات الحميمية",
            "🤝 الإرشاد الزوجي والأسري",
            "🚀 كوتشينغ الأداء والنمو الشخصي"
        ])
        
        mood = st.select_slider("كيف تصف حالتك النفسية اليوم؟", 
                               options=["مرهق", "قلق", "متوسط", "هادئ", "مستقر تماماً"])
        
        description = st.text_area("هل هناك رسالة معينة تود إيصالها قبل الجلسة؟")
        
        st.subheader("⏰ الموعد المفضل")
        col3, col4 = st.columns(2)
        with col3:
            date = st.date_input("اختر اليوم")
        with col4:
            time = st.time_input("التوقيت التقريبي")
        
        st.write("---")
        submitted = st.form_submit_button("إرسال طلب الحجز بكل أمان")
        
        if submitted:
            if name and contact_details:
                conn = sqlite3.connect('consultations_v3.db')
                c = conn.cursor()
                c.execute("""INSERT INTO bookings 
                          (name, age, service, mood, description, contact_method, contact_details, date, time, timestamp) 
                          VALUES (?,?,?,?,?,?,?,?,?,?)""",
                          (name, age, service, mood, description, contact_method, contact_details, str(date), str(time), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success(f"تم استلام طلبك يا {name}. سنقوم بمراسلته عبر {contact_method} لتأكيد الموعد.")
                st.balloons()
            else:
                st.error("الرجاء التأكد من كتابة الاسم ووسيلة التواصل.")

    st.markdown("---")
    st.caption("🔒 جميع بياناتك محمية بموجب السرية المهنية والقانون التونسي لحماية المعطيات الشخصية.")

# --- 4. لوحة تحكم المدير (تحليل البيانات) ---
def admin_page():
    st.sidebar.header("بوابة المدير")
    pwd = st.sidebar.text_input("رمز الدخول", type="password")
    
    if pwd == ADMIN_PASSWORD:
        st.title("📊 لوحة القيادة والتحليل")
        
        conn = sqlite3.connect('consultations_v3.db')
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            # مقاييس ذكاء الأعمال (BI Metrics)
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي الحالات", len(df))
            m2.metric("حالات قلقة/مرهقة", len(df[df['mood'].isin(['مرهق', 'قلق'])]))
            m3.metric("الأكثر طلباً", df['service'].mode()[0].split()[-1])
            
            st.write("---")
            st.subheader("سجل المواعيد المفصل")
            st.dataframe(df.style.background_gradient(cmap='YlOrRd', subset=['age']))
            
            # تصدير البيانات للتحليل الخارجي
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("تحميل تقرير البيانات CSV", csv, "daily_report.csv", "text/csv")
        else:
            st.info("لا توجد حجوزات حتى اللحظة.")
    elif pwd != "":
        st.sidebar.error("الرمز غير صحيح")

# --- 5. التشغيل الرئيسي ---
def main():
    init_db()
    menu = st.sidebar.radio("التنقل", ["فضاء العميل", "الإدارة"])
    
    if menu == "فضاء العميل":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
