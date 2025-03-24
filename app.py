
import streamlit as st
import pandas as pd
import numpy as np
import random

suits = ["♠️ לב שחור", "♥️ לב אדום", "♦️ יהלום", "♣️ תלתן"]
values_display = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

def card_display(value):
    return values_display.get(value, str(value))

def smart_prediction(df):
    last_50 = df.head(50)
    predictions = []

    for suit in ["לב שחור", "לב אדום", "יהלום", "תלתן"]:
        values = last_50[suit].values

        freq_score = pd.Series(values).value_counts().reindex(range(7, 15), fill_value=1).values * 0.2
        trend_score = np.array([
            sum(abs(values[i] - values[i + 1]) <= 2 for i in range(len(values) - 1))
            for card in range(7, 15)
        ]) * 0.25
        diagonal_score = np.random.uniform(0.9, 1.4, size=8) * 0.35
        pull_score = np.array([random.uniform(1, 2.5) for _ in range(7, 15)]) * 0.2

        combined = freq_score + trend_score + diagonal_score + pull_score

        choice = random.choices(range(7, 15), weights=combined, k=1)[0]
        predictions.append(choice)

    return predictions

st.title("🎴 תחזיות צ'אנס חכמות מקובץ CSV")

uploaded_file = st.file_uploader("העלה קובץ CSV עם היסטוריית הגרלות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ הקובץ נטען בהצלחה!")
    st.write("### 50 ההגרלות האחרונות:")
    st.dataframe(df.head(50))

    if st.button("✨ צור 25 תחזיות חכמות"):
        st.markdown("## התחזיות:")
        for idx in range(1, 26):
            result = smart_prediction(df)
            row_display = " | ".join([
                f"{suit} {card_display(card)}" for suit, card in zip(suits, result)
            ])
            st.markdown(f"**תחזית {idx}:** {row_display}")

st.markdown("---")
st.markdown("נבנה על ידי ליביו הוליביה ✅")
