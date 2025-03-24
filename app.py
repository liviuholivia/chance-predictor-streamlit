import streamlit as st
import pandas as pd
import numpy as np
import datetime

# הגדרת הצורות והאייקונים
ordered_suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {"לב שחור": "♠️", "לב אדום": "♥️", "יהלום": "♦️", "תלתן": "♣️"}
allowed_cards = [7, 8, 9, 10, 11, 12, 13, 14]

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

def infer_draw_time(date_str, draw_number):
    date = pd.to_datetime(date_str, dayfirst=True)
    weekday = date.weekday()

    # ראשון עד חמישי - כל שעתיים מ-9:00 עד 21:00 (7 הגרלות ביום)
    if weekday in range(0, 5):
        index = (draw_number - 1) % 7
        time = datetime.time(9 + index * 2, 0)

    # שישי - 3 הגרלות: 10:00, 12:00, 14:00
    elif weekday == 5:
        index = (draw_number - 1) % 3
        time = [datetime.time(10, 0), datetime.time(12, 0), datetime.time(14, 0)][index]

    # שבת - 2 הגרלות: 21:30, 23:00
    elif weekday == 6:
        index = (draw_number - 1) % 2
        time = [datetime.time(21, 30), datetime.time(23, 0)][index]
    else:
        time = datetime.time(0, 0)

    return time.strftime('%H:%M')

st.title("🎴 צירוף שעות הגרלות לפי תאריך והגרלה")
uploaded_file = st.file_uploader("📥 העלה קובץ CSV של 50 הגרלות אחרונות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    df['שעה'] = df.apply(lambda row: infer_draw_time(row['תאריך'], row['מספר הגרלה']), axis=1)

    st.write("### טבלה עם שעות משוערות:")
    st.write(df[['תאריך', 'שעה', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

st.markdown("פותח ע" + "י ליביו הוליביה — עם שעות אוטומטיות לפי דפוסי ההגרלות!")
