import streamlit as st
import pandas as pd
import plotly.express as px
import io
import analytics, pdf_generator


import streamlit as st

st.set_page_config(
    page_title="نظام إدارة المخزون الذكي",
    page_icon="📦",
    layout="wide"
)

st.title("📦 نظام إدارة المخزون الذكي")
# دالة توليد الإكسل الاحترافي (مقسمة لصفحات)
def generate_excel_report(data):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # 1. ورقة الملخص
        stats_df = pd.DataFrame([analytics.get_stats(data)])
        stats_df.to_excel(writer, sheet_name='الملخص', index=False)
        
        # 2. ورقة الراكدة
        analytics.get_stagnant_items(data).to_excel(writer, sheet_name='راكدة', index=False)
        
        # 3. صفحات الفئات A, B, C
        for cat in ['A', 'B', 'C']:
            data[data["تصنيف ABC"] == cat].to_excel(writer, sheet_name=f'فئة {cat}', index=False)
    return buffer.getvalue()

uploaded_file = st.file_uploader("ارفع ملف Excel للمخزون", type=["xlsx"])
if uploaded_file:
    df = analytics.process_inventory(pd.read_excel(uploaded_file))
    
    # 1. تحكم الفئات (الافتراضي هو A)
    if 'cat' not in st.session_state: st.session_state.cat = 'A'
    
    st.write("---")
    # أزرار التحكم بالألوان
    c1, c2, c3 = st.columns(3)
    if c1.button("🔴 فئة A"): st.session_state.cat = 'A'
    if c2.button("🟠 فئة B"): st.session_state.cat = 'B'
    if c3.button("🟢 فئة C"): st.session_state.cat = 'C'


#========================================================================




#=========================================================================

    # 2. عرض الرسوم البيانية
    st.subheader(f"تحليل فئة {st.session_state.cat}")
    col1, col2 = st.columns([1, 2])

    # الرسم الدائري (توزيع القيمة)
    col1.plotly_chart(px.pie(df, names="تصنيف ABC", values="قيمة المخزون", title="توزيع القيمة"), use_container_width=True)
    
    # الرسم البياني للأعمدة (يتغير حسب الفئة المختارة)
    filtered_df = df[df["تصنيف ABC"] == st.session_state.cat].head(10)
    col2.plotly_chart(px.bar(filtered_df, x="الصنف", y="قيمة المخزون", title=f"أعلى 10 أصناف في الفئة {st.session_state.cat}"), use_container_width=True)
    
    # عرض الجدول
    st.dataframe(df[df["تصنيف ABC"] == st.session_state.cat], use_container_width=True)

    # 3. أزرار التصدير
    st.write("---")
    c_ex, c_pd = st.columns(2)
    
    c_ex.download_button(
        "📥 تحميل التقرير الشامل (Excel)", 
        generate_excel_report(df), 
        "Inventory_Report.xlsx"
    )
    
    c_pd.download_button(
        "📥 تحميل التقرير الشامل (PDF)", 
        pdf_generator.create_pdf_report(df, analytics.get_stagnant_items(df)), 
        "Inventory_Report.pdf"
    )
#======================================================================

    import streamlit as st

    # ... بقية كود صفحتك ...

    # تذييل الصفحة
    st.markdown("""
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: transparent;
            color: grey;
            text-align: center;
            padding: 10px;
            font-size: 12px;
        }
        </style>
        <div class="footer">
            <p>المهندس المالي: عزت العصعص | للتواصل: 777884468</p>
        </div>
        """, unsafe_allow_html=True)
    

