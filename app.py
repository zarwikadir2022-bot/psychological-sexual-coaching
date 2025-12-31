import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from PIL import Image # مكتبة للتعامل مع الصور

# --- إعدادات الصفحة (يجب أن تكون في البداية) ---
st.set_page_config(
    page_title="فضاء الاستشارات الآمن",
    page_icon="🌿",
    layout="centered", # يجعل المحتوى في الوسط لتركيز أفضل
    initial_sidebar_state="collapsed"
)

# --- لمسة CSS إضافية لتجميل الأزرار والحواف ---
st.markdown("""
<style>
    /* جعل الحواف دائرية وناعمة */
    .stButton>button {
        border-radius: 20px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px;
    }
    /* تحسين مظهر الرسائل */
    .stAlert {
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

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

# --- 2. إعدادات الأمان ---
ADMIN_PASSWORD = "admin2026" 

# --- 3. فضاء العميل (واجهة جذابة) ---
def client_page():
    # محاولة تحميل صورة الترحيب (تأكد من وجود الملف بجانب الكود)
    try:
        image = Image.open('welcome_img.svg') # أو .png حسب الصورة التي اخترتها
        st.image(image, use_column_width=True)
    except:
        st.write("") # تجاوز إذا لم توجد الصورة

    st.title("🌿 فضاءك الآمن للاستشارة")
    st.markdown("""
    <h4 style='text-align: center; color: #6B6B6B; font-weight: normal;'>
    نحن هنا لنستمع إليك في بيئة تتسم بالدفء، السرية التامة، والاحترافية.
    خطوتك الأولى نحو التوازن تبدأ هنا.
    </h4>
    """, unsafe_allow_html=True)
    st.write("---")
    
    with st.form("consultation_form"):
        st.subheader("📝 معلوماتك الأساسية")
        col1, col2 = st.columns(2) # تقسيم الخانات لتبدو أرتب
        with col1:
            name = st.text_input("الاسم أو اللقب المستعار")
        with col2:
            age = st.number_input("العمر", min_value=18, max_value=90, step=1)
        
        st.subheader("💬 تفاصيل الجلسة")
        service = st.selectbox("نوع الاستشارة التي تبحث عنها", [
            "🧠 استشارة نفسية (قلق، ضغوط، اكتئاب)",
            "❤️ استشارة في الصحة الجنسية والعلاقات",
            "🤝 استشارة زوجية وأسرية",
            "🚀 كوتشينغ أداء وتطوير ذاتي"
        ])
        
        st.write("كيف تشعر اليوم بشكل عام؟")
        mood = st.select_slider("", options=["مرهق جداً", "منخفض الطاقة", "متوسط", "جيد", "ممتاز ومرتاح"], value="متوسط")
        
        description = st.text_area("مساحة حرة: صف لنا باختصار ما ترغب في مناقشته (اختياري)")
        
        st.subheader("📅 الموعد المناسب لك")
        col3, col4 = st.columns(2)
        with col3:
            date = st.date_input("اليوم المفضل")
        with col4:
            time = st.time_input("التوقيت المقترح")
        
        st.write("") # مسافة
        # زر إرسال كبير وواضح
        submitted = st.form_submit_button("تأكيد حجز الجلسة الآن", type="primary")
        
        if submitted:
            if name:
                # محاكاة حفظ البيانات (نفس كود قاعدة البيانات السابق)
                conn = sqlite3.connect('consultations_secure.db')
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, age, service, mood, description, date, time, timestamp) VALUES (?,?,?,?,?,?,?,?)",
                          (name, age, service, mood, description, str(date), str(time), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                
                st.success("✅ شكراً لثقتك. تم استلام طلبك بسرية تامة، سنتواصل معك قريباً لتأكيد الموعد.")
                st.balloons()
            else:
                st.warning("⚠️ يرجى كتابة اسم أو لقب لنتمكن من متابعة طلبك.")

    # سياسة الخصوصية بتصميم هادئ
    st.write("")
    with st.expander("🛡️ التزامنا بالخصوصية والسرية (اضغط للقراءة)"):
        st.markdown("""
        <div style='background-color: #F3F0E7; padding: 15px; border-radius: 10px; font-size: 0.9em;'>
        - <b>السرية المقدسة:</b> بياناتكم محمية بموجب السرية المهنية ولا يتم مشاركتها أبداً.
        - <b>القانون:</b> نلتزم بالقانون التونسي لحماية المعطيات الشخصية.
        - <b>الفضاء الآمن:</b> هذا التطبيق مصمم ليكون مساحة خالية من الأحكام.
        </div>
        """, unsafe_allow_html=True)

# --- 4. لوحة تحكم المدير (بتصميم احترافي) ---
def admin_page():
    st.sidebar.title("🔐 منطقة الإدارة")
    
    # محاولة تحميل صورة الأمان في القائمة الجانبية
    try:
        sidebar_image = Image.open('secure_img.svg') 
        st.sidebar.image(sidebar_image, use_column_width=True)
    except:
        pass

    st.sidebar.write("أدخل كلمة المرور للوصول إلى بيانات العملاء.")
    password_input = st.sidebar.text_input("كلمة المرور", type="password")
    
    if password_input == ADMIN_PASSWORD:
        st.title("📊 لوحة التحليل والمتابعة")
        st.caption("مرحباً أيها الكوتش، إليك نظرة عامة على طلبات الاستشارة.")
        
        conn = sqlite3.connect('consultations_secure.db')
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            # بطاقات إحصائية ملونة
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الحجوزات", len(df), delta="تراكمي")
            
            urgent_cases = len(df[df['mood'] == 'مرهق جداً'])
            col2.metric("حالات تحتاج أولوية", urgent_cases, delta_color="inverse", delta="انتبه لها")
            
            top_service = df['service'].mode()[0] if not df.empty else "N/A"
            col3.metric("الخدمة الأكثر طلباً", top_service.split()[0] + "...") # عرض أول كلمة فقط

            st.write("---")
            st.subheader("📋 سجل الحجوزات الحديثة")
            st.dataframe(df.style.highlight_max(axis=0, color='#E69F8733')) # تلوين خفيف للقيم
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 تصدير البيانات (Excel/CSV)", csv, "consultations.csv", "text/csv")
        else:
            st.info("📭 لا توجد طلبات جديدة حتى الآن. السجل فارغ.")
            
    elif password_input != "":
        st.sidebar.error("⛔ كلمة المرور غير صحيحة.")

# --- 5. التشغيل الرئيسي ---
def main():
    init_db()
    
    # تخصيص القائمة الجانبية
    st.sidebar.title("التنقل")
    choice = st.sidebar.radio("اذهب إلى:", ["صفحة العميل (الحجز)", "لوحة التحكم (للإدارة)"])
    
    st.write("") # مسافة جمالية
    
    if choice == "صفحة العميل (الحجز)":
        client_page()
    else:
        admin_page()

if __name__ == '__main__':
    main()
