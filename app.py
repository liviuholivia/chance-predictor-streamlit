import streamlit as st
import pandas as pd
import numpy as np
import random

suits = ["♠️ לב שחור", "♥️ לב אדום", "♦️ יהלום", "♣️ תלתן"]
values_display = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

# פונקציה שממירה מספרים לאותיות עבור תצוגה

def card_display(value):
    return values_display.get(value, str(value))

# קריאה בטוחה של הקובץ עם קידוד מתאים
uploaded_file = st.file_uploader("📥 העלה קובץ CSV מהארכיון הרשמי:", type=['csv'])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-8')
        st.success("✅ הקובץ נטען בהצלחה!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"⚠️ שגיאה בטעינת הקובץ: {e}")


# אלגוריתם חיזוי מתקדם (דוגמה)
def predict_next(df):
    predictions = []
    last_50 = df.head(50)  # עבודה על 50 ההגרלות האחרונות

    for suit in suits:
        # ניקח ממוצע קלפים לצורה, תוך דגש על מגמות חזקות ומעברי צורות
        mean_card = int(np.round(last_50[suit].mean()))
        adjustment = random.choice([-1, 0, 1])  # שינויים קטנים
        prediction_value = min(14, max(7, mean_card + adjustment))  # רק מ-7 עד A
        predictions.append(prediction_value)

    return predictions

# תצוגת תחזיות
if uploaded_file is not None:
    if st.button("✨ צור תחזית להגרלה הבאה"):
        results = [predict_next(df) for _ in range(25)]  # 25 תחזיות

        st.markdown("## 25 תחזיות:")
        for idx, result in enumerate(results, 1):
            row_display = " | ".join([
                f"{suit} {card_display(card)}" for suit, card in zip(suits, result)
            ])
            st.markdown(f"**תחזית {idx}:** {row_display}")

st.markdown("---")
st.markdown("נבנה על ידי ליביו הוליביה ✅")
