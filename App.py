import streamlit as st

# عنوان التطبيق
st.title("حاسبة الراتب اليومية")

# شرح القواعد
st.write("أدخل عدد الساعات التي عملتها يوميًا، وسنحسب لك الراتب الإجمالي بناءً على القواعد التالية:")
st.write("- 8 ساعات عادية: 14 شيقل/ساعة")
st.write("- الساعات الإضافية: 21 شيقل/ساعة (ساعة ونصف)")
st.write("- يمكنك إضافة ساعات ليوم الجمعة بشكل منفصل (اختياري).")

# تخزين البيانات عبر الجلسات
if 'total_salary' not in st.session_state:
    st.session_state.total_salary = 0.0
if 'total_hours' not in st.session_state:
    st.session_state.total_hours = 0.0
if 'entries' not in st.session_state:
    st.session_state.entries = []

# إدخال عدد الساعات
hours_worked = st.number_input("عدد الساعات التي عملتها اليوم:", min_value=0.0, step=0.5)

# خيار اختياري: هل هذا اليوم هو يوم جمعة؟
is_friday = st.checkbox("هل هذا اليوم هو يوم جمعة؟")

# زر الحساب
if st.button("حساب"):
    # حساب الراتب لهذا اليوم
    regular_rate = 14
    overtime_rate = 21
    friday_rate = 21

    if hours_worked <= 8:
        regular = hours_worked
        overtime = 0
    else:
        regular = 8
        overtime = hours_worked - 8

    salary = (regular * regular_rate) + (overtime * overtime_rate)

    # إذا كان يوم جمعة، نحسب كل الساعات بسعر الجمعة
    if is_friday:
        salary = hours_worked * friday_rate

    # تحديث الإجماليات
    st.session_state.total_salary += salary
    st.session_state.total_hours += hours_worked
    st.session_state.entries.append({
        "hours": hours_worked,
        "is_friday": is_friday,
        "salary": salary
    })

    # عرض نتيجة اليوم الحالي
    st.success(f"تم حساب اليوم: {salary:.2f} شيقل")
    st.info(f"الإجمالي حتى الآن: {st.session_state.total_salary:.2f} شيقل")

# عرض ملخص المدخلات عند الانتهاء
if st.session_state.entries:
    st.subheader("ملخص المدخلات:")
    for idx, entry in enumerate(st.session_state.entries):
        day_type = " (جمعة)" if entry["is_friday"] else ""
        st.write(f"اليوم {idx+1}{day_type}: {entry['hours']} ساعة → {entry['salary']:.2f} شيقل")

    st.subheader("الإجمالي النهائي:")
    st.markdown(f"**عدد الساعات الكلي:** {st.session_state.total_hours:.2f} ساعة")
    st.markdown(f"**الراتب الكلي:** {st.session_state.total_salary:.2f} شيقل")

# زر إعادة التعيين
if st.button("إعادة التشغيل من جديد"):
    st.session_state.total_salary = 0.0
    st.session_state.total_hours = 0.0
    st.session_state.entries = []
    st.experimental_rerun()