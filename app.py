def init_ai():
    if "GOOGLE_API_KEY" not in st.secrets:
        return None
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        
        # كود ذكي للبحث عن الموديل المتاح في حسابك
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # اختيار أفضل موديل متاح (نفضل 1.5 flash)
        target_model = 'models/gemini-1.5-flash'
        if target_model not in available_models:
            # إذا لم يجد الاسم بالمسار الكامل، يبحث عن أي نسخة flash
            flash_models = [m for m in available_models if 'flash' in m]
            target_model = flash_models[0] if flash_models else available_models[0]
            
        return genai.GenerativeModel(target_model)
    except Exception as e:
        st.error(f"⚠️ فشل في العثور على محرك الذكاء الاصطناعي: {e}")
        return None
