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

# פונקציה שמחזירה שעות מדויקות לפי היום בשבוע
def get_hours_for_day(weekday):
    if weekday in [0, 1, 2, 3, 4]:  # ראשון עד חמישי
        return ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"]
    elif weekday == 5:  # שישי
        return ["10:00", "12:00", "14:00"]
    elif weekday == 6:  # שבת
        return ["21:30", "23:00"]

# משייכים לכל הגרלה שעה אמיתית ע"פ רצף אחורה מהתאריך האחרון והמספר האחרון:
def assign_real_hours(df):
    df = df.sort_values("מספר הגרלה", ascending=False).reset_index(drop=True)
    current_date = pd.to_datetime(df.loc[0, 'תאריך'])
    current_weekday = current_date.weekday()
    hours_list = get_hours_for_day(current_weekday)[::-1]

    current_hour_idx = 0
    draw_hours = []

    for i in range(len(df)):
        if current_hour_idx >= len(hours_list):
            current_date -= pd.Timedelta(days=1)
            current_weekday = current_date.weekday()
            hours_list = get_hours_for_day(current_weekday)[::-1]
            current_hour_idx = 0

        draw_hours.append(hours_list[current_hour_idx])
        current_hour_idx += 1

    df['שעה'] = draw_hours
    return df

st.title("🎴 הגרלות צ'אנס — עם שעות מחושבות מדויקות!")
uploaded_file = st.file_uploader("📥 העלה קובץ CSV של 50 הגרלות אחרונות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    df = assign_real_hours(df)

    df_display = df.copy()
    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df_display[suit] = df_display[suit].apply(display_card_value)

    st.write("### טבלת 50 הגרלות עם השעות המחושבות:")
    st.write(df_display[['תאריך', 'שעה', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

st.markdown("פותח על ידי ליביו הוליביה — עם מנגנון השעות הכי מדויק שיש!")
