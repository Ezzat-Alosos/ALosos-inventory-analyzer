import pandas as pd
import datetime

def process_inventory(df):
    df["قيمة المخزون"] = df["الكمية"] * df["سعر الوحدة"]
    df["تاريخ آخر حركة"] = pd.to_datetime(df["تاريخ آخر حركة"])
    today = datetime.datetime.now()
    df["أيام الركود"] = (today - df["تاريخ آخر حركة"]).dt.days
    
    # تصنيف ABC
    df = df.sort_values(by="قيمة المخزون", ascending=False)
    df["نسبة تراكمية"] = df["قيمة المخزون"].cumsum() / df["قيمة المخزون"].sum()
    df["تصنيف ABC"] = pd.cut(df["نسبة تراكمية"], bins=[0, 0.7, 0.9, 1], labels=["A", "B", "C"])
    return df

# هذه الدالة ضرورية لزر التحميل في app.py
def get_stagnant_items(df):
    return df[df["أيام الركود"] > 90]

# هذه الدالة للإحصائيات التي تريد عرضها في الواجهة
def get_stats(df):
    return {
        "إجمالي الأصناف": len(df),
        "إجمالي الكمية": df["الكمية"].sum(),
        "إجمالي القيمة": df["قيمة المخزون"].sum(),
        "أصناف راكدة": len(df[df["أيام الركود"] > 90]),
        "عدد A": len(df[df["تصنيف ABC"] == 'A']),
        "عدد B": len(df[df["تصنيف ABC"] == 'B']),
        "عدد C": len(df[df["تصنيف ABC"] == 'C'])
    }