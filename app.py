import streamlit as st
import pandas as pd
import numpy as np
import datetime

# הגדרות בסיסיות
ordered_suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {"לב שחור": "♠️", "לב אדום": "♥️", "יהלום": "♦️", "תלתן": "♣️"}
allowed_cards = [7, 8, 9, 10, 11, 12, 13, 14]

patterns_impact = {
    "רצף עולה מלא": 1.8,
    "רצף יורד מלא": 1.8,
    "שלישייה זהה בשורה": 2.0,
    "זוג קלפים זהים בשורה": 1.5,
    "קפיצה חדה מאוד בין קלפים": 1.7,
    "סכום שורה מספר ראשוני": 1.4,
    "אלכסון עולה מלא": 2.0,
    "אלכסון יורד מלא": 2.0,
    "שני זוגות שונים בשורה": 1.6,
    "רביעיית קלפים זהים": 3.0,
    "קלף מושך בין שורות": 2.2,
}

pull_relations = {...}
diagonal_relations = {...}

def display_card_value(val):
    return {11: "J", 12: "Q", 13: "K", 14: "A"}.get(val, str(val))

def convert_card_value(value):
    if isinstance(value, str):
        return {"A": 14, "J": 11, "Q": 12, "K": 13}.get(value.strip(), int(value) if value.isdigit() else value)
    return value

# פונקציה לחיזוי כפי שהיה קודם, רק בלי העלאת קובץ דפוסים
def build_weights_with_patterns(df, suit, history_depth):
    recent = df.sort_values('מספר הגרלה', ascending=False).head(history_depth)
    freq = recent[suit].value_counts().reindex(allowed_cards, fill_value=1).values

    pull_factor = np.ones(len(allowed_cards))
    diagonal_factor = np.ones(len(allowed_cards))
    lock_factor = np.ones(len(allowed_cards))
    correction_factor = np.ones(len(allowed_cards))

    last_card = recent.iloc[0][suit]

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

    base = freq * 0.18 + np.random.uniform(0.9, 1.1, size=len(allowed_cards))
    combined = base * pull_factor * 0.3 * diagonal_factor * 0.25 * lock_factor * 0.15 * correction_factor * 0.2

    return combined / combined.sum()

st.title("🎴 אלגוריתם חיזוי דור 3 — אופטימלי וללא קובץ דפוסים")
uploaded_file = st.file_uploader("📥 העלה קובץ CSV של הגרלות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    st.write("### 50 הגרלות אחרונות:")
    last_50 = df.sort_values(by='מספר הגרלה', ascending=False).head(50).copy()
    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        last_50[suit] = last_50[suit].apply(display_card_value)
    last_50 = last_50[['תאריך', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']]
    st.dataframe(last_50)

    history_depth = st.slider("בחר עומק סריקה (מספר הגרלות אחורה):", 50, 1000, 100)

    if st.button("🔄 רענן תחזיות"):
        st.write("### תחזיות חדשות:")
        predictions_data = []

        for i in range(1, 26):
            prediction = []
            for suit in ordered_suits:
                weights = build_weights_with_patterns(df, suit, history_depth)
                chosen = np.random.choice(allowed_cards, p=weights)
                prediction.append({"suit": suit, "card": chosen})

            row = {p['suit']: display_card_value(p['card']) for p in prediction}
            predictions_data.append(row)

        pred_df = pd.DataFrame(predictions_data)[ordered_suits]
        pred_df.columns = [f"{icons[s]} {s}" for s in ordered_suits]

        st.table(pred_df)

st.markdown("פותח על ידי ליביו הוליביה — גרסה ממוקדת, ללא צורך בהעלאת קובץ דפוסים!")
