def admin_page():
    st.sidebar.header("بوابة المدير")
    pwd = st.sidebar.text_input("رمز الدخول", type="password")
    
    if pwd == ADMIN_PASSWORD:
        st.title("📊 لوحة القيادة والتحليل البصري")
        
        conn = sqlite3.connect('consultations_v3.db')
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not df.empty:
            # --- الإحصائيات السريعة ---
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي الحالات", len(df))
            m2.metric("حالات قلقة/مرهقة", len(df[df['mood'].isin(['مرهق', 'قلق'])]))
            m3.metric("أكثر تخصص مطلوب", df['service'].mode()[0].split()[-1])
            
            st.write("---")

            # --- القسم الجديد: الرسوم البيانية ---
            st.subheader("📈 التحليل الإحصائي للمواعيد")
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.write("**توزيع أنواع الاستشارات**")
                service_counts = df['service'].value_counts()
                st.bar_chart(service_counts)

            with col_chart2:
                st.write("**تحليل الحالات المزاجية**")
                mood_counts = df['mood'].value_counts()
                st.write("يعطيك فكرة عن الحالة العامة للمرضى")
                st.line_chart(mood_counts)

            st.write("---")
            
            # --- جدول البيانات ---
            st.subheader("📋 سجل المواعيد المفصل")
            st.dataframe(df)
            
            # تصدير البيانات
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("تحميل تقرير البيانات CSV", csv, "daily_report.csv", "text/csv")
        else:
            st.info("لا توجد حجوزات حتى اللحظة لتمثيلها بيانياً.")
    elif pwd != "":
        st.sidebar.error("الرمز غير صحيح")
