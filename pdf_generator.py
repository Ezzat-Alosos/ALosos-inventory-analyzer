from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
import io
import os
from datetime import datetime
from reportlab.pdfgen import canvas
# تسجيل الخط العربي (تأكد أن الملف في نفس المجلد)
font_path = os.path.join(os.path.dirname(__file__), 'ARIAL.TTF')
pdfmetrics.registerFont(TTFont('ArabicFont', font_path))

def ar(text):
    return get_display(arabic_reshaper.reshape(str(text)))



#=========================================================

class LastPageFooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        total_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            # آخر صفحة فقط
            if self._pageNumber == total_pages:
                self.saveState()
                self.setFont(
                    "ArabicFont",
                    9
                )
                self.setFillColor(
                    colors.grey
                )
                text = ar(
                    "المهندس المالي: عزت العصعص | للتواصل: 777884468"
                )
                self.drawCentredString(
                    letter[0] / 2,
                    25,
                    text
                )
                self.restoreState()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

#=========================================================



def create_pdf_report(df, stagnant_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
   
    # تنسيقات
    title_style = ParagraphStyle('Title', fontName='ArabicFont', fontSize=24, alignment=1)
    h1_style = ParagraphStyle('H1', fontName='ArabicFont', fontSize=18, spaceBefore=20, spaceAfter=15, textColor=colors.navy)
    normal_style = ParagraphStyle('Normal', fontName='ArabicFont', fontSize=12, alignment=1)

    # 1. الترويسة (الاسم فوق، التاريخ والوقت تحته)
    elements.append(Paragraph(ar("العصعص لتحليل المخزون"), title_style))
    elements.append(Spacer(1, 17)) # مسافة إضافية بين العنوان والتاريخ
    elements.append(Paragraph(ar(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d')} | وقت الإنشاء: {datetime.now().strftime('%H:%M:%S')}"), normal_style))
    elements.append(Spacer(1, 30))

    # 2. الملخص التنفيذي (شامل)
    elements.append(Paragraph(ar("الملخص التنفيذي"), h1_style))
    summary_data = [
        [ar("المؤشر"), ar("القيمة")],
        [ar("إجمالي الأصناف"), str(len(df))],
        [ar("إجمالي الكمية"), f"{df['الكمية'].sum():,.0f}"],
        [ar("إجمالي القيمة"), f"{df['قيمة المخزون'].sum():,.2f}"],
        [ar("عدد الأصناف الراكدة"), str(len(stagnant_df))],
        [ar("عدد أصناف A"), str(len(df[df['تصنيف ABC'] == 'A']))],
        [ar("عدد أصناف B"), str(len(df[df['تصنيف ABC'] == 'B']))],
        [ar("عدد أصناف C"), str(len(df[df['تصنيف ABC'] == 'C']))]
    ]
    t = Table(summary_data, colWidths=[200, 150])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black), ('FONTNAME', (0,0), (-1,-1), 'ArabicFont'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(t)
    elements.append(PageBreak())

    # 3. الأقسام (الفئات)
    # 3. قسم تحليل ABC المدمج (في صفحة واحدة)
    elements.append(Paragraph(ar("تحليل المخزون ABC"), h1_style))
    
    # أولاً: مخطط أعمدة مقارنة ABC
    abc_summary = df.groupby('تصنيف ABC')['قيمة المخزون'].sum().reindex(['A', 'B', 'C'])
    plt.figure(figsize=(6, 3))
    colors_list = ['#FF0000', '#FFA500', '#008000']
    bars = plt.bar(abc_summary.index, abc_summary.values, color=colors_list)
    plt.title(ar("إجمالي قيمة المخزون لكل فئة"))
    
    # إضافة القيم فوق الأعمدة
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:,.0f}', ha='center', va='bottom', fontsize=9)
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    elements.append(Image(img_buffer, width=350, height=180))
    plt.close()

    # ثانياً: جدول مقارنة ABC
    total_val = df['قيمة المخزون'].sum()
    table_data = [[ar("الفئة"), ar("عدد الأصناف"), ar("الكمية"), ar("القيمة"), ar("النسبة %")]]
    for i, cat in enumerate(['A', 'B', 'C']):
        cat_df = df[df['تصنيف ABC'] == cat]
        table_data.append([cat, str(len(cat_df)), f"{cat_df['الكمية'].sum():,.0f}", f"{cat_df['قيمة المخزون'].sum():,.2f}", f"{(cat_df['قيمة المخزون'].sum()/total_val)*100:.1f}%"])
    
    t = Table(table_data, colWidths=[60, 80, 80, 100, 80])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,-1), 'ArabicFont')]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # ثالثاً: جداول الأصناف (3 جداول بجانب بعض)
    # ثالثاً: جداول الأصناف (بدون تسطير في العناوين وتنسيق أنظف)
    sub_tables = []
    headers = [ar("فئة A"), ar("فئة B"), ar("فئة C")]
    colors_list = [colors.red, colors.orange, colors.green]
    
    for i, cat in enumerate(['A', 'B', 'C']):
        cat_data = df[df["تصنيف ABC"] == cat].head(10)
        
        # دمج العنوان مع البيانات في جدول واحد
        data = [[headers[i], "", ""], [ar("الصنف"), ar("الكمية"), ar("القيمة")]]
        for _, row in cat_data.iterrows():
            data.append([ar(str(row['الصنف'])), str(row['الكمية']), f"{row['قيمة المخزون']:.0f}"])
        
        st = Table(data, colWidths=[60, 40, 50])
        st.setStyle(TableStyle([
            ('SPAN', (0, 0), (2, 0)),
            # 1. تسطير كامل للبيانات (من الصف الثاني فما تحت - أي صف العناوين والبيانات)
            ('GRID', (0, 1), (-1, -1), 0.2, colors.black),
            
            # 2. إزالة الخط الفاصل بين العنوان الملون وصف العناوين (الصنف، الكمية، القيمة)
            # نقوم بذلك عن طريق تحديد GRID لصف العنوان بشكل منفصل أو ببساطة عدم شموله في GRID
            
            
            
            # 3. تنسيق العنوان الملون (الخلية الأولى فقط من الصف الأول)
            ('BACKGROUND', (0, 0), (2, 0), colors_list[i]),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.white),
            ('ALIGN', (0, 0), (2, 0), 'CENTER'),
            ('VALIGN', (0, 0), (2, 0), 'MIDDLE'),


            # <<< أضف هذا السطر هنا لتكبير خط العنوان فقط >>>
            ('FONTSIZE', (0, 0), (5, 0), 16),
            

            # تنسيق النص والخطوط
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
            # 4. تنسيق صف رؤوس الجدول (الصنف، الكمية، القيمة)
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke), # اختياري: خلفية خفيفة لصف الرؤوس
        ]))
        sub_tables.append(st)
    
    # دمج الجداول الثلاثة في صف واحد
    elements.append(Table([sub_tables], colWidths=[150, 150, 150]))
    elements.append(PageBreak())

    doc.build(
    elements,
    canvasmaker=LastPageFooterCanvas
)

    return buffer.getvalue()

