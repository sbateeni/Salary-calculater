import streamlit as st
import pandas as pd
import json
import os

# اسم ملف JSON
JSON_FILE = "data.json"

# تحميل البيانات من ملف JSON
def load_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# حفظ البيانات إلى ملف JSON
def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تحميل البيانات
data = load_data()

# تحويلها إلى DataFrame
df = pd.DataFrame(data)

# واجهة المستخدم
st.title("حساب الأجور باستخدام JSON")

# إدخال البيانات الجديدة
st.subheader("إضافة بيانات جديدة")
new_day = st.text_input("اليوم")
new_date = st.date_input("التاريخ")
new_start = st.time_input("ساعة الدخول")
new_end = st.time_input("ساعة الخروج")

if st.button("إضافة"):
    if new_day and new_start and new_end:
        entry = {
            "اليوم": new_day,
            "تاريخ": str(new_date),
            "ساعة الدخول": str(new_start),
            "ساعة الخروج": str(new_end)
        }
        data.append(entry)
        save_data(data)
        st.success("تمت الإضافة بنجاح!")
        st.experimental_rerun()

# حذف بيانات
st.subheader("حذف سجل معين")
if len(data) > 0:
    delete_options = [f'{entry["اليوم"]} - {entry["تاريخ"]}' for entry in data]
    selected_entry = st.selectbox("اختر سجلًا للحذف", delete_options)

    if st.button("حذف"):
        for entry in data:
            if f'{entry["اليوم"]} - {entry["تاريخ"]}' == selected_entry:
                data.remove(entry)
                save_data(data)
                st.success("تم حذف السجل بنجاح!")
                st.experimental_rerun()

# حساب الأجور
if len(data) > 0:
    df["ساعة الدخول"] = pd.to_datetime(df["ساعة الدخول"], format="%H:%M:%S")
    df["ساعة الخروج"] = pd.to_datetime(df["ساعة الخروج"], format="%H:%M:%S")
    df["مجموع الساعات"] = (df["ساعة الخروج"] - df["ساعة الدخول"]).dt.total_seconds() / 3600
    df["حتى 8 ساعات"] = df["مجموع الساعات"].apply(lambda x: min(x, 8))
    df["الساعات الزائدة"] = df["مجموع الساعات"].apply(lambda x: max(x - 8, 0))

    # حساب الأجور
    hourly_rate = 14  # سعر الساعة العادية
    overtime_rate = hourly_rate * 1.5  # سعر الساعة الإضافية

    df["أجر الساعات العادية"] = df["حتى 8 ساعات"] * hourly_rate
    df["أجر الساعات الزائدة"] = df["الساعات الزائدة"] * overtime_rate
    df["إجمالي الأجر"] = df["أجر الساعات العادية"] + df["أجر الساعات الزائدة"]

    # تجميع الأجور حسب الشهر
    df["الشهر"] = pd.to_datetime(df["تاريخ"]).dt.month
    monthly_summary = df.groupby("الشهر")[["حتى 8 ساعات", "الساعات الزائدة", "إجمالي الأجر"]].sum()

    # عرض البيانات
    st.subheader("جدول البيانات المحسوبة")
    st.dataframe(df)

    st.subheader("إجمالي الأجور لكل شهر")
    st.dataframe(monthly_summary)

    total_salary = monthly_summary["إجمالي الأجر"].sum()
    st.subheader(f"إجمالي الأجر الكلي: {total_salary:.2f} شيقل")