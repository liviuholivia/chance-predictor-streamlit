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

# פונקציה לבחירה הסתברותית חכמה

def weighted_random_choice(values, weights, used_cards):
    total = sum(weights)
    for _ in range(20):
        r = random.uniform(0, total)
        upto = 0
        for val, w in zip(values, weights):
            if upto + w >= r:
                if val not in used_cards:
                    return val
                break
            upto += w
    candidates = [(val, w) for val, w in zip(values, weights) if val not in used_cards]
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0] if candidates else random.choice(values)

# אלגוריתם עם מניעת כפילויות ומיון לפי סדר הצורות הקבוע

def generate_prediction(num_cards, df=None, single_suit=None):
    cards = []
    used_cards = set()
    suits_to_use = [single_suit] if single_suit else suits[:num_cards]

    for suit_name in suits_to_use:
        values = range(1, 14)
        if df is not None:
            col_index = suits.index(suit_name) + 2
            col_name = df.columns[col_index]
            freq_series = df[col_name].value_counts().reindex(range(1, 14), fill_value=1).values
        else:
            freq_series = np.random.uniform(0.5, 2.0, size=13)

        trend_boost = np.random.uniform(0.8, 2.8, size=13)
        explosive_factor = np.random.uniform(1.0, 4.0, size=13)
        time_factor = np.random.uniform(0.9, 1.2, size=13)

        combined_weights = freq_series * 0.4 + trend_boost * 0.35 + explosive_factor * 0.2 + time_factor * 0.05

        chosen_card = weighted_random_choice(values, combined_weights, used_cards)
        used_cards.add(chosen_card)
        cards.append({"suit": suit_name, "card": chosen_card})

    # מיון התוצאות לפי הסדר הקבוע של הצורות
    cards.sort(key=lambda x: suits.index(x['suit']))
    return cards


def generate_options(num_cards, options_count=6, df=None, single_suit=None):
    return [generate_prediction(num_cards, df, single_suit) for _ in range(options_count)]

# Streamlit UI
st.set_page_config(page_title="חיזוי חכם לצ'אנס", page_icon="🎴", layout="centered")
st.title("🎴 חיזוי חכם ומסודר להגרלות צ׳אנס")
st.markdown("בחר מספר קלפים, אפשר להעלות קובץ CSV, ולנתח צורה מסוימת אם בחרת קלף אחד.")

uploaded_file = st.file_uploader("📥 העלה קובץ CSV עם היסטוריית הגרלות (לא חובה):", type=["csv"])
df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
        df.columns = ["תאריך", "מספר הגרלה", "תלתן", "יהלום", "לב אדום", "לב שחור", "ריק"]
        st.success("✅ הקובץ נטען בהצלחה!")
        st.dataframe(df.drop(columns=["ריק"]).head())
    except Exception as e:
        st.error(f"❗ שגיאה בטעינת הקובץ: {e}")

num_cards = st.radio("📊 בחר כמה קלפים לנתח:", [1, 2, 3, 4], index=3, horizontal=True)
single_suit = None

if num_cards == 1:
    single_suit = st.selectbox("בחר את הצורה לחיזוי:", suits)

if st.button("✨ צור תחזית מקצועית"):
    options = generate_options(num_cards, df=df, single_suit=single_suit)

    for idx, option in enumerate(options, 1):
        st.markdown(f"#### 🃏 תחזית מלאה לאפשרות {idx}")
        pretty_line = " | ".join([
            f"{icons[item['suit']]} {item['suit']}: {'A' if item['card'] == 1 else 'J' if item['card'] == 11 else 'Q' if item['card'] == 12 else 'K' if item['card'] == 13 else item['card']}"
            for item in option
        ])
        st.markdown(f"**{pretty_line}**")

        for item in option:
            card_display = "A" if item['card'] == 1 else "J" if item['card'] == 11 else "Q" if item['card'] == 12 else "K" if item['card'] == 13 else item['card']
            st.write(f"{icons[item['suit']]} {item['suit']}: {card_display}")

st.markdown("---")
st.markdown("### 📖 מדריך שימוש:")
st.markdown("""
- העלה קובץ CSV עם היסטוריית הגרלות (לא חובה).
- בחר כמה קלפים תרצה לנתח (1, 2, 3 או 4).
- אם בחרת קלף אחד — תוכל לבחור את הצורה (תלתן, יהלום, לב אדום, לב שחור).
- לחץ על 'צור תחזית מקצועית'.
- יוצגו 6 תחזיות שונות, מסודרות תמיד לפי הסדר: תלתן, יהלום, לב אדום, לב שחור.
""")
