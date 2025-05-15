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
            df = pd.DataFrame(data)
            # تحويل التاريخ إلى datetime لتجنب الأخطاء
            df['التاريخ الميلادي'] = pd.to_datetime(df['التاريخ الميلادي'], errors='coerce')
            return df
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


# --- واجهة المستخدم ---
st.set_page_config(layout="wide")
st.title("حاسبة المرتبات - مع دعم JSON")

st.markdown("يمكنك إضافة أو تعديل البيانات أدناه. يتم حفظ البيانات في ملف `data.json`. يمكنك إضافة أيام جديدة شهريًا.")

# --- تحميل البيانات ---
df = load_data()

# --- ضمان أن التاريخ بصيغة صحيحة ---
if not df.empty:
    df['التاريخ الميلادي'] = pd.to_datetime(df['التاريخ الميلادي'], errors='coerce')

# --- جدول التحرير ---
st.subheader("تحرير البيانات")
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    column_config={
        "التاريخ الميلادي": st.column_config.DateColumn(
            "التاريخ الميلادي",
            format="YYYY-MM-DD",
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31),
            default=datetime.today()
        ),
        "وقت الدخول": st.column_config.TextColumn("وقت الدخول", default="00:00"),
        "وقت الخروج": st.column_config.TextColumn("وقت الخروج", default="00:00"),
        "عدد الساعات": st.column_config.NumberColumn("عدد الساعات", step=0.1),
        "الساعات العادية": st.column_config.NumberColumn("الساعات العادية", step=0.1),
        "الساعات الإضافية": st.column_config.NumberColumn("الساعات الإضافية", step=0.1),
        "تكلفة العادية": st.column_config.NumberColumn("تكلفة العادية", step=1.0),
        "تكلفة الإضافية": st.column_config.NumberColumn("تكلفة الإضافية", step=1.0),
        "التكلفة الكلية": st.column_config.NumberColumn("التكلفة الكلية", step=1.0),
        "الساعات المحتسبة": st.column_config.NumberColumn("الساعات المحتسبة", step=0.1)
    },
    use_container_width=True
)

# --- زر الحفظ ---
if st.button("💾 حفظ البيانات"):
    # تحويل التاريخ إلى نص قبل الحفظ
    edited_df['التاريخ الميلادي'] = pd.to_datetime(edited_df['التاريخ الميلادي'], errors='coerce').dt.strftime('%Y-%m-%d')
    edited_df.fillna({
        'وقت الدخول': '00:00',
        'وقت الخروج': '00:00',
        'عدد الساعات': 0,
        'الساعات العادية': 0,
        'الساعات الإضافية': 0,
        'تكلفة العادية': 0,
        'تكلفة الإضافية': 0,
        'التكلفة الكلية': 0,
        'الساعات المحتسبة': 0
    }, inplace=True)

    # حفظ البيانات
    data_to_save = edited_df.copy()
    save_data(data_to_save)
    st.success("✅ تم حفظ البيانات بنجاح في ملف data.json")


# --- جدول إحصائي شهري ---
if not edited_df.empty:
    edited_df['التاريخ الميلادي'] = pd.to_datetime(edited_df['التاريخ الميلادي'], errors='coerce')
    edited_df['الشهر'] = edited_df['التاريخ الميلادي'].dt.strftime('%B %Y')  # أبريل 2025

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
        for eng, arabic in month_map.items():
            if eng in month_en:
                return arabic + month_en[month_en.find(' '):]
        return month_en

    edited_df['الشهر'] = edited_df['الشهر'].apply(rename_month)

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

    csv_full = convert_df(edited_df.drop(columns=['الشهر'], errors='ignore'))
    csv_monthly = convert_df(monthly_stats)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 تحميل الجدول كـ CSV", data=csv_full, file_name="الجدول_النهائي.csv", mime="text/csv")
    with col2:
        st.download_button("📊 تحميل الإحصائيات الشهرية", data=csv_monthly, file_name="الاحصائيات_الشهرية.csv", mime="text/csv")
else:
    st.warning("⚠️ لا توجد بيانات بعد. أضف بعض السجلات لتحصل على تحليل شهري.")