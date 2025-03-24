import streamlit as st
import pandas as pd
import numpy as np

# הגדרת הצורות והאייקונים
ordered_suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {"לב שחור": "♠️", "לב אדום": "♥️", "יהלום": "♦️", "תלתן": "♣️"}
allowed_cards = [7, 8, 9, 10, 11, 12, 13, 1]  # מ-7 עד אס

# פונקציות המרה להצגת קלפים
def display_card_value(val):
    return {1: "A", 11: "J", 12: "Q", 13: "K"}.get(val, str(val))

def convert_card_value(value):
    if isinstance(value, str):
        if value.strip() == 'A': return 1
        elif value.strip() == 'J': return 11
        elif value.strip() == 'Q': return 12
        elif value.strip() == 'K': return 13
        elif value.isdigit(): return int(value)
    return value

# משיכות, אלכסונים, תיקונים ונעילות משולבים:
pull_relations = {
    7: [8, 10, 11],
    8: [9, 11, 13],
    9: [10, 12, 13],
    10: [7, 1, 11],
    11: [9, 13, 10],
    12: [11, 9, 1],
    13: [1, 10, 8],
    1: [9, 12, 10]
}

diagonal_relations = {
    7: [9, 10, 13], 8: [10, 11, 12], 9: [11, 13, 7],
    10: [7, 9, 1], 11: [9, 12, 7], 12: [10, 13, 8],
    13: [7, 10, 1], 1: [9, 11, 12]
}

def build_weights(df, suit):
    recent = df.sort_values('מספר הגרלה', ascending=False).head(50)
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
                    pull_factor[allowed_cards.index(pull_card)] += 2

        if card in diagonal_relations:
            for diag in diagonal_relations[card]:
                if diag in allowed_cards:
                    diagonal_factor[allowed_cards.index(diag)] += 1.8

        if card == last_card:
            lock_factor[idx] += 2.5  # נעילה

        if abs(card - last_card) >= 4:
            correction_factor[idx] += 3  # תיקון לקפיצה חריגה

    base = freq * 0.15 + np.random.uniform(0.9, 1.1, size=len(allowed_cards))
    combined = base * pull_factor * 0.3 * diagonal_factor * 0.25 * lock_factor * 0.15 * correction_factor * 0.15

    return combined / combined.sum()

def predict_next(df):
    prediction = []
    for suit in ordered_suits:
        weights = build_weights(df, suit)
        chosen = np.random.choice(allowed_cards, p=weights)
        prediction.append({"suit": suit, "card": chosen})
    return prediction

st.title("🎴 אלגוריתם סופר חכם להגרלות צ'אנס — גרסה מעודכנת")
uploaded_file = st.file_uploader("📥 העלה קובץ CSV של 50 הגרלות אחרונות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    df = df.sort_values(by='מספר הגרלה', ascending=False).head(50)
    st.write(df[['תאריך', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

    st.write("### 25 תחזיות:")
    for i in range(1, 26):
        prediction = predict_next(df)
        row_str = " | ".join([f"{icons[p['suit']]} {display_card_value(p['card'])}" for p in prediction])
        st.write(f"**תחזית {i}: {row_str}**")

st.markdown("פותח ע" + "י ליביו הוליביה — גרסה מעודכנת על פי כל הדפוסים שנלמדו!")
