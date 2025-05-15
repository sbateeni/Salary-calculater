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
            return json.load(f).get("البيانات", [])  # تجنب حدوث خطأ إذا لم يكن المفتاح موجودًا
    return []

# حفظ البيانات إلى ملف JSON
def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({"البيانات": data}, f, ensure_ascii=False, indent=4)

# تحميل البيانات
data = load_data()

st.title("إدارة سجلات الأجور")

# حذف بيانات بشكل آمن
st.subheader("حذف سجل معين")

if len(data) > 0:
    # تأكد من أن الإدخالات تحتوي على المفتاحين "اليوم" و"تاريخ"
    delete_options = [f'{entry.get("اليوم", "غير محدد")} - {entry.get("تاريخ", "غير محدد")}' for entry in data]
    selected_entry = st.selectbox("اختر سجلًا للحذف", delete_options)

    if st.button("حذف"):
        # البحث عن الإدخال ومقارنته مع خيار المستخدم
        for entry in data:
            if f'{entry.get("اليوم", "غير محدد")} - {entry.get("تاريخ", "غير محدد")}' == selected_entry:
                data.remove(entry)
                save_data(data)
                st.success("تم حذف السجل بنجاح!")
                st.experimental_rerun()
else:
    st.warning("لا توجد سجلات للحذف.")