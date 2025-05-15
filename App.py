import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# --- إعدادات ---
DATA_FILE = "data.json"

# --- دوال المساعدة ---
def time_to_decimal(t):
    h, m = map(int, t.split(':'))
    return h + m / 60

def calculate_hours(entry, exit_time):
    start = datetime.strptime(entry, "%H:%M")
    end = datetime.strptime(exit_time, "%H:%M")
    delta = (end - start).seconds / 3600
    if delta < 0:
        delta += 24  # لدعم الدوام الليلي
    return round(delta, 2)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f).get("entries", [])
            df = pd.DataFrame(data)
            return df
    else:
        return pd.DataFrame(columns=[
            "التاريخ الميلادي", "وقت الدخول", "وقت الخروج",
            "عدد الساعات", "الساعات العادية", "الساعات الإضافية",
            "تكلفة العادية", "تكلفة الإضافية", "التكلفة الكلية", "الساعات المحتسبة"
        ])

# --- واجهة المستخدم ---
st.set_page_config(layout="wide")
st.title("حاسبة المرتبات - مع إعادة الحساب التلقائي")

st.markdown("يتم الآن إعادة الحساب التلقائي للراتب بناءً على قواعد العمل: 14 شيكل للساعة العادية، 21 شيكل للساعة الإضافية.")

# --- تحميل البيانات ---
df = load_data()

if not df.empty:
    # --- إعادة الحساب التلقائي ---
    updated_rows = []
    for _, row in df.iterrows():
        date_str = row["التاريخ الميلادي"]
        entry = row["وقت الدخول"]
        exit_t = row["وقت الخروج"]

        if pd.isna(date_str) or pd.isna(entry) or pd.isna(exit_t):
            continue

        hours_worked = calculate_hours(entry, exit_t)
        regular = min(hours_worked, 8)
        extra = max(0, hours_worked - 8)
        cost_regular = regular * 14
        cost_extra = extra * 21
        total_cost = cost_regular + cost_extra
        counted_hours = regular + extra * 1.5

        updated_rows.append({
            "التاريخ الميلادي": date_str,
            "وقت الدخول": entry,
            "وقت الخروج": exit_t,
            "عدد الساعات": hours_worked,
            "الساعات العادية": regular,
            "الساعات الإضافية": extra,
            "تكلفة العادية": cost_regular,
            "تكلفة الإضافية": cost_extra,
            "التكلفة الكلية": total_cost,
            "الساعات المحتسبة": counted_hours
        })

    if updated_rows:
        final_df = pd.DataFrame(updated_rows)

        # --- استخلاص الشهر ---
        final_df['التاريخ الميلادي'] = pd.to_datetime(final_df['التاريخ الميلادي'], errors='coerce')
        final_df['الشهر'] = final_df['التاريخ الميلادي'].dt.strftime('%B %Y')

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

        def rename_month(month_en):
            return month_map.get(month_en.split()[0], month_en) + " " + month_en.split()[1]

        final_df['الشهر'] = final_df['الشهر'].apply(rename_month)

        # --- عرض الجدول النهائي ---
        st.subheader("📊 الجدول النهائي بعد الحساب التلقائي")
        st.dataframe(final_df.drop(columns=['الشهر']), use_container_width=True)

        # --- إحصائيات شهرية ---
        monthly_stats = final_df.groupby("الشهر").agg(
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

        csv_full = convert_df(final_df)
        csv_monthly = convert_df(monthly_stats)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 تحميل الجدول كـ CSV", data=csv_full, file_name="الجدول_النهائي.csv", mime="text/csv")
        with col2:
            st.download_button("📊 تحميل الإحصائيات الشهرية", data=csv_monthly, file_name="الاحصائيات_الشهرية.csv", mime="text/csv")

        # --- عرض الإجمالي العام ---
        total_regular = monthly_stats["مجموع_الساعات_العاديه"].sum()
        total_extra = monthly_stats["مجموع_الساعات_الإضافية"].sum()
        total_salary = monthly_stats["مجموع_التكاليف"].sum()

        st.markdown("---")
        st.subheader("💰 الإجمالي العام")
        col1, col2, col3 = st.columns(3)
        col1.metric("مجموع الساعات العادية", f"{total_regular:.2f} ساعة")
        col2.metric("مجموع الساعات الإضافية", f"{total_extra:.2f} ساعة")
        col3.metric("الراتب الإجمالي الشهري", f"{total_salary:.2f} شيكل")

else:
    st.warning("⚠️ لا توجد بيانات في ملف JSON. تأكد من وجود بيانات صحيحة.")