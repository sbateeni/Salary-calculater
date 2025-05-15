import streamlit as st

# عنوان التطبيق
st.title("حاسبة الراتب اليومية")

st.write("أدخل عدد الساعات التي عملتها يوميًا، وسنحسب لك الراتب الإجمالي بناءً على القواعد التالية:")
st.write("- 8 ساعات عادية: 14 شيقل/ساعة")
st.write("- الساعات الإضافية: 21 شيقل/ساعة (ساعة ونصف)")
st.write("- يمكنك إضافة ساعات ليوم الجمعة بشكل منفصل (اختياري).")

# تهيئة الحالة
if 'total_salary' not in st.session_state:
    st.session_state.total_salary = 0.0
if 'total_hours' not in st.session_state:
    st.session_state.total_hours = 0.0
if 'entries' not in st.session_state:
    st.session_state.entries = []

# استخدام مفتاح مميز للحقل، مع عدم استخدام session_state لتغييره يدوياً
hours_worked = st.number_input("عدد الساعات التي عملتها اليوم:", min_value=0.0, step=0.5, key="hours_input")
is_friday = st.checkbox("هل هذا اليوم هو يوم جمعة؟", key="friday_input")

# زر الحساب
if st.button("حساب"):
    if hours_worked > 0:
        # الحساب
        regular_rate = 14
        overtime_rate = 21
        friday_rate = 21

        if is_friday:
            salary = hours_worked * friday_rate
        else:
            if hours_worked <= 8:
                salary = hours_worked * regular_rate
            else:
                salary = (8 * regular_rate) + ((hours_worked - 8) * overtime_rate)

        # التحديث
        st.session_state.total_salary += salary
        st.session_state.total_hours += hours_worked
        st.session_state.entries.append({
            "hours": hours_worked,
            "is_friday": is_friday,
            "salary": salary
        })

        st.success(f"تم حساب اليوم: {salary:.2f} شيقل")
        st.info(f"الإجمالي حتى الآن: {st.session_state.total_salary:.2f} شيقل")

        # إعادة ضبط المدخلات باستخدام إعادة التشغيل
        st.experimental_rerun()

# عرض الملخص
if st.session_state.entries:
    st.subheader("ملخص المدخلات:")
    for idx, entry in enumerate(st.session_state.entries):
        day_type = " (جمعة)" if entry["is_friday"] else ""
        st.write(f"اليوم {idx+1}{day_type}: {entry['hours']} ساعة → {entry['salary']:.2f} شيقل")

    st.subheader("الإجمالي النهائي:")
    st.markdown(f"**عدد الساعات الكلي:** {st.session_state.total_hours:.2f} ساعة")
    st.markdown(f"**الراتب الكلي:** {st.session_state.total_salary:.2f} شيقل")

# زر التراجع
if st.button("التراجع عن الإضافة الأخيرة"):
    if st.session_state.entries:
        last_entry = st.session_state.entries.pop()
        st.session_state.total_salary -= last_entry["salary"]
        st.session_state.total_hours -= last_entry["hours"]
        st.success("تم التراجع عن آخر إضافة.")
        st.experimental_rerun()

# زر إعادة التشغيل
if st.button("إعادة التشغيل من جديد"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()