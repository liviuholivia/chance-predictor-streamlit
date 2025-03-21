
import streamlit as st
import pandas as pd
import random
import numpy as np

suits = ["תלתן", "יהלום", "לב אדום", "לב שחור"]
icons = {
    "לב שחור": "♠️", 
    "לב אדום": "♥️",
    "יהלום": "♦️",
    "תלתן": "♣️",
}

def weighted_random_choice(values, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for val, w in zip(values, weights):
        if upto + w >= r:
            return val
        upto += w

def generate_advanced_prediction(num_cards, df=None):
    cards = []
    for i in range(num_cards):
        values = range(1, 14)

        if df is not None:
            col_name = df.columns[2 + i]
            freq_series = df[col_name].value_counts().reindex(range(1, 14), fill_value=1).values
        else:
            freq_series = np.random.uniform(0.5, 2.0, size=13)

        trend_boost = np.random.uniform(0.8, 2.8, size=13)
        explosive_factor = np.random.uniform(1.0, 4.0, size=13)
        time_factor = np.random.uniform(0.9, 1.2, size=13)

        combined_weights = freq_series * 0.4 + trend_boost * 0.35 + explosive_factor * 0.2 + time_factor * 0.05
        chosen_card = weighted_random_choice(values, combined_weights)

        cards.append({"suit": suits[i], "card": chosen_card})

    return cards

def generate_advanced_options(num_cards, options_count=6, df=None):
    return [generate_advanced_prediction(num_cards, df) for _ in range(options_count)]

st.title("🎯 חיזוי חכם ומשופר להגרלות צ׳אנס")
st.markdown("בחר את מספר הקלפים, העלה קובץ CSV אם יש לך, ולחץ על יצירת תחזיות.")

uploaded_file = st.file_uploader("העלה קובץ CSV עם נתוני הגרלות (לא חובה):", type=["csv"])
df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
        st.success("✅ הקובץ נטען בהצלחה!")
        st.write(df.head())
    except Exception as e:
        st.error(f"שגיאה בטעינת הקובץ: {e}")

num_cards = st.radio("בחר מספר קלפים:", [1, 2, 3, 4], index=3, horizontal=True)

if st.button("צור תחזית מקצועית"):
    options = generate_advanced_options(num_cards, df=df)

    for idx, option in enumerate(options, 1):
        st.subheader(f"אפשרות {idx}")
        for item in option:
            card_display = "A" if item['card'] == 1 else "J" if item['card'] == 11 else "Q" if item['card'] == 12 else "K" if item['card'] == 13 else item['card']
            st.write(f"{icons[item['suit']]} {item['suit']}: {card_display}")

st.markdown("---")
st.markdown("""
### 📖 מדריך שימוש משודרג:
- ניתן להעלות קובץ CSV עם היסטוריית הגרלות.
- בחר את מספר הקלפים (1, 2, 3 או 4).
- לחץ על כפתור "צור תחזית מקצועית".
- האלגוריתם ישתמש בנתונים שלך אם קיימים.
- יוצגו 6 אפשרויות תחזית מגוונות.
- מוצג לפי סדר: תלתן, יהלום, לב אדום, לב שחור.
""")
