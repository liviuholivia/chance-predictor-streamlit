import streamlit as st
import pandas as pd
import random
import numpy as np

suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {
    "לב שחור": "♠️", 
    "לב אדום": "♥️",
    "יהלום": "♦️",
    "תלתן": "♣️",
}

# פונקציה לבחירה הסתברותית חכמה במיוחד
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

# פונקציה לאלגוריתם סופר מתקדם עם כל הדפוסים

def calculate_super_trend_bonus(df, suit_name):
    values = range(1, 14)
    col_index = suits.index(suit_name) + 2
    column_values = df.iloc[:, col_index].values[:50]
    bonus_weights = np.ones(13)

    for i in range(len(column_values) - 3):
        diff1 = column_values[i + 1] - column_values[i]
        diff2 = column_values[i + 2] - column_values[i + 1]

        # אלכסונים
        if abs(diff1) == 1 and abs(diff2) == 1 and (diff1 == diff2):
            next_val = column_values[i + 2] + diff2
            if 1 <= next_val <= 13:
                bonus_weights[next_val - 1] += 2.0

        # מדרגות הפוכות
        if diff1 < 0 and diff2 < 0:
            next_val = column_values[i + 2] + 3
            if next_val <= 13:
                bonus_weights[next_val - 1] += 2.5

        # חזרתיות תוך 3–5 הגרלות
        last_occurrences = df.iloc[i:i+5, 2:6].values.flatten()
        for val in values:
            if val in last_occurrences:
                bonus_weights[val - 1] += 1.4

        # זוגי/אי זוגי מתחלף
        recent_val = column_values[i]
        for val in values:
            if (val % 2) != (recent_val % 2):
                bonus_weights[val - 1] += 0.9

        # שיקוף עמודות
        for val in values:
            row_values = df.iloc[i:i+4, 2:6].values.flatten()
            if val in row_values:
                bonus_weights[val - 1] += 1.3

        # קלפים ראשוניים
        for prime in [2, 3, 5, 7, 11]:
            bonus_weights[prime - 1] += 1.2

        # אפקט ריבאונד
        if column_values[i] in [11, 12, 13]:
            for mid in range(5, 10):
                bonus_weights[mid - 1] += 1.5

    return bonus_weights

# האלגוריתם הסופר-מדהים!
def generate_prediction(suits_to_use, df=None):
    cards = []
    used_cards = set()

    for suit_name in suits_to_use:
        values = range(1, 14)
        if df is not None:
            col_index = suits.index(suit_name) + 2
            col_name = df.columns[col_index]
            freq_series = df[col_name].value_counts().reindex(range(1, 14), fill_value=1).values
            super_bonus = calculate_super_trend_bonus(df, suit_name)
        else:
            freq_series = np.random.uniform(0.5, 2.0, size=13)
            super_bonus = np.ones(13)

        trend_boost = np.random.uniform(0.8, 2.8, size=13)
        explosive_factor = np.random.uniform(1.0, 4.0, size=13)
        time_factor = np.random.uniform(0.9, 1.2, size=13)

        combined_weights = freq_series * 0.25 + trend_boost * 0.25 + explosive_factor * 0.2 + time_factor * 0.05 + super_bonus * 0.25

        chosen_card = weighted_random_choice(values, combined_weights, used_cards)
        used_cards.add(chosen_card)
        cards.append({"suit": suit_name, "card": chosen_card})

    cards.sort(key=lambda x: suits.index(x['suit']))
    return cards


def generate_options(suits_to_use, options_count=6, df=None):
    return [generate_prediction(suits_to_use, df) for _ in range(options_count)]

# Streamlit UI
st.set_page_config(page_title="מנוע חיזוי סופר חכם להגרלות צ׳אנס", page_icon="🎴", layout="centered")
st.title("🎴 מנוע חיזוי סופר חכם ומקצועי!")

st.markdown("""<p style='text-align:center;'>האלגוריתם מבוסס על ניתוח סטטיסטי, מגמות, רצפים אלכסוניים, שיקופים, ראשוניים, אפקט ריבאונד וחזרתיות — לניבוי ההגרלה הבאה. נבנה על ידי ליביו הוליביה.</p>""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📥 העלה קובץ CSV עם היסטוריית הגרלות (לא חובה):", type=["csv"])
df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
        df.columns = ["תאריך", "מספר הגרלה", "לב שחור", "לב אדום", "יהלום", "תלתן", "ריק"]
        st.success("✅ הקובץ נטען בהצלחה!")
        st.dataframe(df.drop(columns=["ריק"]).head())
    except Exception as e:
        st.error(f"❗ שגיאה בטעינת הקובץ: {e}")

num_cards = st.radio("📊 בחר כמה קלפים לנתח:", [1, 2, 3, 4], index=3, horizontal=True)
selected_suits = st.multiselect("בחר את הצורות לניתוח:", suits, default=suits[:num_cards])

if st.button("✨ צור תחזית סופר חכמה"):
    if len(selected_suits) != num_cards:
        st.warning("אנא בחר מספר צורות זהה למספר הקלפים שבחרת.")
    else:
        options = generate_options(selected_suits, df=df)

        for idx, option in enumerate(options, 1):
            st.markdown(f"#### 🃏 תחזית לאפשרות {idx}")

            table_data = {f"{icons[item['suit']]} {item['suit']}": [
                "A" if item['card'] == 1 else "J" if item['card'] == 11 else "Q" if item['card'] == 12 else "K" if item['card'] == 13 else item['card']
                ] for item in option
            }
            table_df = pd.DataFrame(table_data)
            st.table(table_df)

st.markdown("---")
st.markdown("### 📖 איך האלגוריתם עובד:")
st.markdown("""
- ניתוח 50 ההגרלות האחרונות.
- שקלול שכיחויות, מגמות אלכסוניות, מדרגות, שיקופים, מספרים ראשוניים וריבאונדים.
- התאמה לזוגי/אי זוגי מתחלף.
- ניבוי חכם להגרלה הבאה.
- נבנה על ידי ליביו הוליביה.
""")
