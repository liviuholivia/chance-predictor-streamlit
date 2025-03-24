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
        if value.strip() == 'A':
            return 14
        elif value.strip() == 'J':
            return 11
        elif value.strip() == 'Q':
            return 12
        elif value.strip() == 'K':
            return 13
        elif value.isdigit():
            return int(value)
    return value


# פונקציה שמחזירה את השעה לפי מס' הגרלה, יום ותאריך
def calculate_draw_time(date, draw_index):
    weekday = date.weekday()
    if weekday in range(0, 5):  # ראשון עד חמישי
        draw_times = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"]
        return draw_times[draw_index % len(draw_times)]
    elif weekday == 5:  # שישי
        draw_times = ["10:00", "12:00", "14:00"]
        return draw_times[draw_index % len(draw_times)]
    elif weekday == 6:  # שבת
        draw_times = ["21:30", "23:00"]
        return draw_times[draw_index % len(draw_times)]


# בניית השעות לאחור לפי רצף הגרלות
def assign_times(df):
    df = df.sort_values("מספר הגרלה", ascending=True).reset_index(drop=True)
    current_date = pd.to_datetime(df.iloc[-1]["תאריך"], dayfirst=True)
    draw_counter = 0

    draw_times = []
    for index, row in df.iterrows():
        if index > 0 and row["מספר הגרלה"] != df.iloc[index - 1]["מספר הגרלה"] + 1:
            current_date -= pd.Timedelta(days=1)
            draw_counter = 0
        draw_times.append(calculate_draw_time(current_date, draw_counter))
        draw_counter += 1

    df["שעה"] = draw_times
    df = df.sort_values("מספר הגרלה", ascending=False).reset_index(drop=True)
    return df


st.title("🎴 צירוף שעות אוטומטי להגרלות צ'אנס")

uploaded_file = st.file_uploader("📥 העלה קובץ CSV של 50 הגרלות אחרונות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    df = assign_times(df)

    st.write("### טבלה עם שעות משוקללות ואמיתיות לפי תבנית:")
    df_display = df.copy()
    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df_display[suit] = df_display[suit].apply(display_card_value)

    st.write(df_display[['תאריך', 'שעה', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

st.markdown("פותח על ידי ליביו הוליביה — עכשיו מסונכרן סופית לפי רצף, ימים ושעות!")
