import streamlit as st

# العنوان الرئيسي للتطبيق
st.title("حاسبة الراتب")

# شرح التطبيق
st.write("أدخل عدد الساعات التي عملتها، وستحسب لك القيمة بناءً على القواعد التالية:")
st.write("- كل ساعة ≤ 8 ساعات: 14 شيقل.")
st.write("- الساعات الإضافية (بعد 8 ساعات): 21 شيقل (1.5 × 14).")
st.write("- إذا عملت في يوم الجمعة، فإن كل ساعة تُحسب بقيمة 21 شيقل.")

# إدخال عدد الساعات العادية
total_hours = st.number_input("أدخل عدد الساعات التي عملتها:", min_value=0.0, step=0.5)

# إدخال عدد الساعات في يوم الجمعة (اختياري)
friday_hours = st.number_input("أدخل عدد الساعات التي عملتها في يوم الجمعة (إذا كان هناك):", min_value=0.0, step=0.5)

# حساب الراتب
def calculate_salary(total_hours, friday_hours):
    # قيم الساعات
    regular_hour_rate = 14  # قيمة الساعة العادية
    overtime_hour_rate = 21  # قيمة الساعة الإضافية (1.5 × 14)
    friday_hour_rate = 21  # قيمة الساعة في يوم الجمعة

    # حساب الساعات العادية والساعات الإضافية
    if total_hours <= 8:
        regular_hours = total_hours
        overtime_hours = 0
    else:
        regular_hours = 8
        overtime_hours = total_hours - 8

    # حساب الراتب
    salary = (
        (regular_hours * regular_hour_rate) +  # الراتب من الساعات العادية
        (overtime_hours * overtime_hour_rate) +  # الراتب من الساعات الإضافية
        (friday_hours * friday_hour_rate)  # الراتب من يوم الجمعة
    )

    return salary

# حساب الراتب بناءً على المدخلات
salary = calculate_salary(total_hours, friday_hours)

# عرض النتيجة
st.write(f"**الراتب الإجمالي:** {salary:.2f} شيقل")
