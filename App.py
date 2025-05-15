import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# --- إعدادات ---
DATA_FILE = "data.json"

# --- دوال المساعدة ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f).get("entries", [])
            return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "التاريخ الميلادي", "وقت الدخول", "وقت الخروج",
            "عدد الساعات", "الساعات العادية", "الساعات الإضافية",
            "تكلفة العادية", "تكلفة الإضافية", "التكلفة الكلية", "الساعات المحتسبة"
        ])

def save_data(df):
    data = {"entries": df.to_dict(orient="records")}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def time_to_decimal(t):
    h, m = map(int, t.split(':'))
    return h + m / 60

def calculate_hours(entry, exit_time):
    start = datetime.strptime(entry, "%H:%M")
    end = datetime.strptime(exit_time, "%H:%M")
    delta = (end - start).seconds / 3600
    if delta < 0:
        delta += 24
    return round(delta, 2)

day_map = {
    "Saturday": "السبت",
    "Sunday": "الأحد",
    "Monday": "الاثنين",
    "Tuesday": "الثلاثاء",
    "Wednesday": "الأربعاء",
    "Thursday": "الخميس",
    "Friday": "الجمعة"
}

# --- واجهة المستخدم ---
st.set_page_config(layout="wide")
st.title("حاسبة المرتبات - مع دعم JSON")

st.markdown("يمكنك إضافة أو تعديل البيانات أدناه. يتم حفظ البيانات في ملف `data.json`. يمكنك إضافة أيام جديدة شهريًا.")

# --- تحميل البيانات ---
df = load_data()

# --- تحويل عمود التاريخ إلى datetime لتفادي تعارض type ---
df['التاريخ الميلادي'] = pd.to_datetime(df['التاريخ الميلادي'], errors='coerce')

# --- جدول التحرير ---
st.subheader("تحرير البيانات")
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    column_config={
        "التاريخ الميلادي": st.column_config.DateColumn("التاريخ الميلادي", format="YYYY-MM-DD"),
        "وقت الدخول": st.column_config.TimeColumn("وقت الدخول", format="HH:mm"),
        "وقت الخروج": st.column_config.TimeColumn("وقت الخروج", format="HH:mm")
    },
    use_container_width=True
)

# --- زر الحفظ ---
if st.button("💾 حفظ البيانات"):
    save_data(edited_df)
    st.success("✅ تم حفظ البيانات بنجاح في ملف data.json")

# --- تحديث الحسابات ---
if not edited_df.empty:
    # تحويل التاريخ إلى datetime
    edited_df['التاريخ الميلادي'] = pd.to_datetime(edited_df['التاريخ الميلادي'], errors='coerce')

    # إضافة عمود الشهر بصيغة "أبريل 2025"
    edited_df['الشهر'] = edited_df['التاريخ الميلادي'].dt.strftime('%B %Y')  # مثلاً: April 2025

    # إعادة تسمية الأشهر بالعربية (اختياري)
    month_map = {
        'January': 'يناير',
        'February': 'فبراير',
        'March': 'مارس',
        'April': 'أبريل',
        'May': 'مايو',
        'June': 'يونيو',
        'July': 'يوليو',
        'August': 'أغسطس',
        'September': 'سبتمبر',
        'October': 'أكتوبر',
        'November': 'نوفمبر',
        'December': 'ديسمبر'
    }

    # دالة لتغيير اسم الشهر إلى العربية
    def rename_month(month_en):
        for eng, arabic in month_map.items():
            if eng in month_en:
                return arabic + month_en[month_en.find(' '):]
        return month_en

    edited_df['الشهر'] = edited_df['الشهر'].apply(rename_month)

    # --- عرض الجدول النهائي ---
    st.subheader("📊 الجدول النهائي بعد التحديث")
    st.dataframe(edited_df.drop(columns=['الشهر'], errors='ignore'), use_container_width=True)

    # --- إحصائيات شهرية ---
    monthly_stats = edited_df.groupby("الشهر").agg(
        مجموع_الساعات_العاديه=("الساعات العادية", "sum"),
        مجموع_الساعات_الإضافية=("الساعات الإضافية", "sum"),
        مجموع_التكاليف=("التكلفة الكلية", "sum")
    ).reset_index()

    st.subheader("📅 إحصائيات شهرية")
    st.dataframe(monthly_stats, use_container_width=True)

    # --- تنزيل CSV ---
    @st.cache_data
    def convert_df(data):
        return data.to_csv(index=False).encode('utf-8')

    csv_full = convert_df(edited_df)
    csv_monthly = convert_df(monthly_stats)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 تحميل الجدول كـ CSV", data=csv_full, file_name="الجدول_النهائي.csv", mime="text/csv")
    with col2:
        st.download_button("📅 تحميل الإحصائيات الشهرية", data=csv_monthly, file_name="الاحصائيات_الشهرية.csv", mime="text/csv")
else:
    st.warning("يرجى إدخال البيانات أولاً.")