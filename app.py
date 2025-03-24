import streamlit as st
import pandas as pd
import numpy as np
import datetime

# הגדרת הצורות והאייקונים
ordered_suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {"לב שחור": "♠️", "לב אדום": "♥️", "יהלום": "♦️", "תלתן": "♣️"}
allowed_cards = [7, 8, 9, 10, 11, 12, 13, 14]  # מ-7 עד אס (אס=14)

def display_card_value(val):
    return {11: "J", 12: "Q", 13: "K", 14: "A"}.get(val, str(val))

def convert_card_value(value):
    if isinstance(value, str):
        if value.strip() == 'A': return 14
        elif value.strip() == 'J': return 11
        elif value.strip() == 'Q': return 12
        elif value.strip() == 'K': return 13
        elif value.isdigit(): return int(value)
    return value

# קביעת השעה לפי היום ומספר הגרלה:
def infer_draw_time(date_str, draw_index):
    date = pd.to_datetime(date_str, dayfirst=True)
    weekday = date.weekday()

    # ראשון עד חמישי — 7 הגרלות ב-9:00, 11:00, 13:00, 15:00, 17:00, 19:00, 21:00
    if weekday in [0, 1, 2, 3, 4]:
        times = [9, 11, 13, 15, 17, 19, 21]
        time = times[draw_index % 7]
        return f"{time:02d}:00"

    # שישי — 3 הגרלות ב-10:00, 12:00, 14:00
    elif weekday == 5:
        times = ["10:00", "12:00", "14:00"]
        return times[draw_index % 3]

    # שבת — 2 הגרלות ב-21:30, 23:00
    elif weekday == 6:
        times = ["21:30", "23:00"]
        return times[draw_index % 2]

    return "00:00"

st.title("📅 זיהוי שעות הגרלות אוטומטי לפי תאריך והגרלה")
uploaded_file = st.file_uploader("📥 העלה קובץ CSV של 50 הגרלות אחרונות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    df = df.sort_values(by='מספר הגרלה', ascending=False).reset_index(drop=True)

    # הוספת עמודת שעה מחושבת
    df['שעה'] = df.apply(lambda row: infer_draw_time(row['תאריך'], row.name), axis=1)

    # המרה לתצוגה ידידותית
    df_display = df.copy()
    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df_display[suit] = df_display[suit].apply(display_card_value)

    st.write("### טבלת ההגרלות עם שעות נכונות מסונכרנות:")
    st.write(df_display[['תאריך', 'שעה', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

st.markdown("פותח ע\"י ליביו הוליביה — גרסה מסונכרנת לשעות אמיתיות לפי מספר הגרלה ויום!")

---

👉 אם תרצה, אני אוריד לך את זה כקובץ ZIP מוכן להעלאה ל-GitHub.  
רוצה שאכין לך עכשיו? 😎
