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

def infer_draw_time_accurate(start_draw_number, start_datetime, draw_number):
    diff = start_draw_number - draw_number
    current_time = start_datetime
    while diff > 0:
        weekday = current_time.weekday()
        if weekday in range(0, 5):  # ראשון עד חמישי: 7 הגרלות ביום ב-9:00,11:00,13:00,15:00,17:00,19:00,21:00
            draws_today = [9, 11, 13, 15, 17, 19, 21]
        elif weekday == 5:  # שישי: 3 הגרלות 10:00, 12:00, 14:00
            draws_today = [10, 12, 14]
        else:  # שבת: 2 הגרלות 21:30, 23:00
            draws_today = [21.5, 23]

        draws_today.sort(reverse=True)
        for draw_hour in draws_today:
            if diff == 0:
                break
            current_time = current_time - datetime.timedelta(hours=draw_hour if isinstance(draw_hour, int) else 0, minutes=30 if draw_hour % 1 != 0 else 0)
            diff -= 1
    return current_time.strftime('%H:%M')

st.title("🎴 הגרלות עם זיהוי שעות לפי סדר מדויק")
uploaded_file = st.file_uploader("📥 העלה קובץ CSV של 50 הגרלות אחרונות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    # קביעת נקודת עוגן (למשל: הגרלה נוכחית 50732 ב-24/03/2025 בשעה 19:00)
    anchor_draw_number = 50732
    anchor_date = datetime.datetime.strptime("24/03/2025 19:00", "%d/%m/%Y %H:%M")

    df['שעה'] = df.apply(lambda row: infer_draw_time_accurate(anchor_draw_number, anchor_date, row['מספר הגרלה']), axis=1)

    st.write("### טבלה מסונכרנת עם שעות מדויקות:")
    df_display = df.copy()
    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df_display[suit] = df_display[suit].apply(display_card_value)

    st.write(df_display[['תאריך', 'שעה', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

st.markdown("פותח על ידי ליביו הוליביה — עכשיו הכל מסונכרן כמו שצריך!")
