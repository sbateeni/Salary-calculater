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
    # إعادة الحساب
    updated_rows = []
    for _, row in edited_df.iterrows():
        date_str = row["التاريخ الميلادي"].strftime("%Y-%m-%d") if not pd.isna(row["التاريخ الميلادي"]) else None
        entry = row["وقت الدخول"].strftime("%H:%M") if not pd.isna(row["وقت الدخول"]) else None
        exit_t = row["وقت الخروج"].strftime("%H:%M") if not pd.isna(row["وقت الخروج"]) else None

        if date_str and entry and exit_t:
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
        df_updated = pd.DataFrame(updated_rows)

        # --- عرض الجدول النهائي ---
        st.subheader("📊 الجدول النهائي بعد التحديث")
        st.dataframe(df_updated, use_container_width=True)

        # --- إحصائيات شهرية ---
        df_updated['الشهر'] = pd.to_datetime(df_updated['التاريخ الميلادي']).dt.to_period('M').astype(str)
        monthly_stats = df_updated.groupby("الشهر").agg(
            مجموع_الساعات_العاديه=("الساعات العادية", "sum"),
            مجموع_الساعات_الإضافية=("الساعات الإضافية", "sum"),
            مجموع_التكاليف=("التكلفة الكلية", "sum"),
            مجموع_الساعات_المحتسبه=("الساعات المحتسبة", "sum")
        ).reset_index()

        st.subheader("📅 إحصائيات شهرية")
        st.dataframe(monthly_stats, use_container_width=True)

        # --- تنزيل CSV ---
        @st.cache_data
        def convert_df(data):
            return data.to_csv(index=False).encode('utf-8')

        csv_full = convert_df(df_updated)
        csv_monthly = convert_df(monthly_stats)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 تحميل الجدول كـ CSV", data=csv_full, file_name="الجدول_النهائي.csv", mime="text/csv")
        with col2:
            st.download_button("📅 تحميل الإحصائيات الشهرية", data=csv_monthly, file_name="الاحصائيات_الشهرية.csv", mime="text/csv")