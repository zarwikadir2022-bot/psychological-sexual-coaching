import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. إعداد الصفحة (يجب أن يكون أول أمر إلزامي) ---
st.set_page_config(
    page_title="فضاء الاستشارة والنمو 2026",
    page_icon="🌿",
    layout="centered"
)

# --- 2. إعداد قاعدة البيانات (نسخة v4 لضمان ثبات الهيكل) ---
DB_NAME = 'consultations_v4.db'

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

# --- 3. الألوان والجمالية (CSS) ---
st.markdown("""
<style>
    .stButton>button {
        border-radius: 20px;
        background-color: #E69F87;
        color: white;
        width: 100%;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    .main {
        background-color: #FDFCF8;
    }
    .trust-box {
        background-color: #F3F0E7;
        padding: 20px;
        border-radius: 15px;
        border-right: 5px solid #E69F87;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. فضاء العميل (واجهة الحجز) ---
def client_page():
    st.title("🌿 فضاءك الآمن للاستشارة")
    st.markdown("<h4 style='color: #6B6B6B; font-weight: normal;'>خطوتك الأولى نحو التوازن النفسي والانسجام تبدأ من هنا.</h4>", unsafe_allow_html=True)
    
    with st.form("booking_form"):
        st.subheader("📌 المعلومات الأساسية")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم أو اللقب المستعار")
        with col2:
            age = st.number_input("العمر", min_value=18, max_value=100, step=1)
        
        st.subheader("📞 وسيلة التواصل")
        c_col1, c_col2 = st.columns([1, 2])
        with c_col1:
            method = st.radio("تواصل عبر:", ["واتساب/هاتف", "إيميل"])
        with c_col2:
            details = st.text_input("رقم الهاتف أو عنوان البريد الإلكتروني")

        st.subheader("🔍 تفاصيل الجلسة")
        service = st.selectbox("مجال الاستشارة المطلوب", [
            "🧠 التوازن النفسي وإدارة الضغوط",
            "❤️ الصحة الجنسية والعلاقات",
            "🤝 الإرشاد الزوجي والأسري",
            "🚀 كوتشينغ الأداء والنمو الشخصي"
        ])
        
        mood = st.select_slider("كيف تصف حالتك النفسية اليوم؟", 
                               options=["مرهق", "قلق", "متوسط", "هادئ", "مستقر"])
        
        description = st.text_area("وصف موجز لما ترغب في مناقشته (اختياري)")
        
        st.subheader("⏰ الموعد المفضل")
        col3, col4 = st.columns(2)
        with col3:
            date = st.date_input("اختر اليوم")
        with col4:
            time = st.time_input("التوقيت التقريبي")
        
        submitted = st.form_submit_button("إرسال طلب الحجز بكل أمان")
        
        if submitted:
            if name and details:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("""INSERT INTO bookings 
                          (name, age, service, mood, description, contact_method, contact_details, date, time, timestamp) 
                          VALUES (?,?,?,?,?,?,?,?,?,?)""",
                          (name, age, service, mood, description, method, details, str(date), str(time), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success(f"✅ تم استلام طلبك يا {name}. سنتواصل معك عبر {method} قريباً.")
                st.balloons()
            else:
                st.error("⚠️ يرجى التأكد من ملء الاسم ووسيلة التواصل.")

    # ميثاق الثقة والخصوصية
    st.markdown("""
    <div class="trust-box">
        <h5 style="color: #4A4A4A;">🛡️ ميثاق الثقة والخصوصية:</h5>
        <p style="color: #6B6B6B; font-size: 0.9em;">
        • <b>السرية المهنية:</b> معلوماتك وجلساتك سر مقدّس لا يطلع عليه أحد.<br>
        • <b>الإطار القانوني:</b> المعطيات الشخصية محمية وفق القانون التونسي عدد 63 لسنة 2004.<br>
        • <b>الأمان الرقمي:</b> بياناتك مشفرة ومخزنة في بيئة تقنية آمنة.<br>
        • <b>فضاء بدون أحكام:</b> مساحة آمنة للتعبير بحرية تامة.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. لوحة التحكم (الإدارة والتحليل) ---
def admin_page():
    st.sidebar.title("🔐 بوابة المدير")
    pwd = st.sidebar.text_input("أدخل رمز الدخول", type="password")
    
    if pwd == "admin2026":
        st.title("📊 لوحة قيادة الاستشارات")
        
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            # مقاييس سريعة
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي الحجوزات", len(df))
            m2.metric("حالات قلقة/مرهقة", len(df[df['mood'].isin(['مرهق', 'قلق'])]))
            m3.metric("أكثر تخصص طلباً", df['service'].mode()[0].split()[-1])
            
            st.write("---")
            st.subheader("📈 التحليل البصري")
            st.bar_chart(df['service'].value_counts())
            
            st.subheader("📋 السجل التفصيلي")
            st.dataframe(df)
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تحميل التقرير الشامل CSV", csv, "consultations_2026.csv", "text/csv")
        else:
            st.info("لا توجد حجوزات مسجلة حتى الآن.")
    elif pwd != "":
        st.sidebar.error("الرمز غير صحيح")

# --- 6. التشغيل الرئيسي ---
def main():
    init_db()
    menu = st.sidebar.radio("التنقل", ["فضاء العميل", "لوحة التحكم"])
    
    if menu == "فضاء العميل":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
