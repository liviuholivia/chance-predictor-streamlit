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

def get_draw_hour(date, draw_index, day_of_week):
    # מיפוי שעות לפי יום בשבוע
    if day_of_week in [0,1,2,3,4]:  # ראשון עד חמישי
        schedule = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"]
    elif day_of_week == 5:  # שישי
        schedule = ["10:00", "12:00", "14:00"]
    else:  # שבת
        schedule = ["21:30", "23:00"]

    return schedule[draw_index % len(schedule)]

# חיזוקים לפי משיכות, אלכסונים, נעילות, קפיצות ויום-שעה
pull_relations = {
    7: [8, 9, 10, 11, 14], 8: [9, 11, 13, 14], 9: [10, 12, 13, 14],
    10: [7, 14, 11, 9], 11: [9, 13, 10, 8], 12: [11, 9, 14, 10],
    13: [14, 10, 8, 9], 14: [9, 12, 10, 7]
}

diagonal_relations = {
    7: [9, 10, 13, 14], 8: [10, 11, 12, 14], 9: [11, 13, 7, 14],
    10: [7, 9, 14, 12], 11: [9, 12, 7, 14], 12: [10, 13, 8, 14],
    13: [7, 10, 14, 9], 14: [9, 11, 12, 10]
}

def build_weights(df, suit):
    recent = df.sort_values('מספר הגרלה', ascending=False).head(50)
    freq = recent[suit].value_counts().reindex(allowed_cards, fill_value=1).values

    pull_factor = np.ones(len(allowed_cards))
    diagonal_factor = np.ones(len(allowed_cards))
    lock_factor = np.ones(len(allowed_cards))
    correction_factor = np.ones(len(allowed_cards))

    last_row = recent.iloc[0]
    last_card = last_row[suit]
    last_date = pd.to_datetime(last_row['תאריך'])
    weekday = last_date.weekday()
    draw_index = 0  # מתוך מיון, זו ההגרלה האחרונה

    hour_str = get_draw_hour(last_date, draw_index, weekday)

    for idx, card in enumerate(allowed_cards):
        if card in pull_relations:
            for pull_card in pull_relations[card]:
                if pull_card in allowed_cards:
                    pull_factor[allowed_cards.index(pull_card)] += 2.2

        if card in diagonal_relations:
            for diag in diagonal_relations[card]:
                if diag in allowed_cards:
                    diagonal_factor[allowed_cards.index(diag)] += 2

        if card == last_card:
            lock_factor[idx] += 2.7

        if abs(card - last_card) >= 4:
            correction_factor[idx] += 3.5

        # חיזוק לפי שעה ביום
        hour = int(hour_str.split(":")[0])
        if 9 <= hour <= 12 and suit in ["תלתן", "לב שחור"]:
            pull_factor[idx] += 1.6
        if 19 <= hour <= 23 and suit in ["לב אדום", "יהלום"]:
            correction_factor[idx] += 1.8

    base = freq * 0.18 + np.random.uniform(0.9, 1.1, size=len(allowed_cards))
    combined = base * pull_factor * 0.3 * diagonal_factor * 0.25 * lock_factor * 0.15 * correction_factor * 0.2

    return combined / combined.sum()

def predict_next(df):
    prediction = []
    for suit in ordered_suits:
        weights = build_weights(df, suit)
        chosen = np.random.choice(allowed_cards, p=weights)
        prediction.append({"suit": suit, "card": chosen})
    return prediction

st.title("🎴 אלגוריתם סופר חכם לצ'אנס עם זיהוי שעות! — גרסה מקצועית")
uploaded_file = st.file_uploader("📥 העלה קובץ CSV של 50 הגרלות אחרונות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    df = df.sort_values(by='מספר הגרלה', ascending=False).head(50)

    st.write("### טבלת 50 הגרלות אחרונות:")
    st.write(df[['תאריך', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

    st.write("### 25 תחזיות בטבלה:")
    predictions_data = []
    for i in range(1, 26):
        prediction = predict_next(df)
        row = {p['suit']: display_card_value(p['card']) for p in prediction}
        predictions_data.append(row)

    pred_df = pd.DataFrame(predictions_data)
    pred_df = pred_df[ordered_suits]
    pred_df.columns = [f"{icons[s]} {s}" for s in ordered_suits]

    st.table(pred_df)

st.markdown("פותח ע" + "י ליביו הוליביה — גרסה עם חיזוק לפי שעה, יום וכל הדפוסים שנלמדו!")
