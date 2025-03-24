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

def infer_draw_time(date_str, draw_index, weekday):
    if weekday in range(0, 5):  # ראשון עד חמישי
        times = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"]
        return times[draw_index % len(times)]

    elif weekday == 5:  # שישי
        times = ["10:00", "12:00", "14:00"]
        return times[draw_index % len(times)]

    elif weekday == 6:  # שבת
        times = ["21:30", "23:00"]
        return times[draw_index % len(times)]

    return "00:00"

st.title("🎴 טבלת הגרלות עם שעות מדויקות לפי יום ושיטה!")
uploaded_file = st.file_uploader("📥 העלה קובץ CSV של 50 הגרלות אחרונות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    df = df.sort_values(by='מספר הגרלה', ascending=True).reset_index(drop=True)

    # חישוב שעות לפי הגרלות
    df['שעה'] = df.apply(
        lambda row: infer_draw_time(
            row['תאריך'],
            df[df['תאריך'] == row['תאריך']].index.get_loc(row.name),
            pd.to_datetime(row['תאריך'], dayfirst=True).weekday()
        ),
        axis=1
    )

    df = df.sort_values(by='מספר הגרלה', ascending=False).reset_index(drop=True)

    df_display = df.copy()
    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df_display[suit] = df_display[suit].apply(display_card_value)

    st.write("### טבלה מסונכרנת עם שעות הגרלה מדויקות:")
    st.write(df_display[['תאריך', 'שעה', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

st.markdown("פותח ע" + "י ליביו הוליביה — עם סנכרון שעות אוטומטי מדויק!")
