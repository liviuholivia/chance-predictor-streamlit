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

# פונקציה להמרת קלפים מאותיות למספרים
def convert_card_value(value):
    if isinstance(value, str):
        value = value.strip()
        if value == 'A':
            return 1
        elif value == 'J':
            return 11
        elif value == 'Q':
            return 12
        elif value == 'K':
            return 13
        elif value.isdigit():
            return int(value)
    return value

# פונקציה לחישוב בונוס סופר חכם
def calculate_super_trend_bonus(df, suit_column):
    values = range(1, 14)
    column_values = df[suit_column].apply(convert_card_value).values[:50]
    bonus_weights = np.ones(13)

    for i in range(len(column_values) - 3):
        diff1 = column_values[i + 1] - column_values[i]
        diff2 = column_values[i + 2] - column_values[i + 1]

        if abs(diff1) == 1 and abs(diff2) == 1 and (diff1 == diff2):
            next_val = column_values[i + 2] + diff2
            if 1 <= next_val <= 13:
                bonus_weights[next_val - 1] += 2.0

        if diff1 < 0 and diff2 < 0:
            next_val = column_values[i + 2] + 3
            if next_val <= 13:
                bonus_weights[next_val - 1] += 2.5

        last_occurrences = df.iloc[i:i+5].applymap(convert_card_value).values.flatten()
        for val in values:
            if val in last_occurrences:
                bonus_weights[val - 1] += 1.4

        recent_val = column_values[i]
        for val in values:
            if (val % 2) != (recent_val % 2):
                bonus_weights[val - 1] += 0.9

        row_values = df.iloc[i:i+4].applymap(convert_card_value).values.flatten()
        for val in values:
            if val in row_values:
                bonus_weights[val - 1] += 1.3

        for prime in [2, 3, 5, 7, 11]:
            bonus_weights[prime - 1] += 1.2

        if column_values[i] in [11, 12, 13]:
            for mid in range(5, 10):
                bonus_weights[mid - 1] += 1.5

    return bonus_weights

# אלגוריתם מותאם למבנה הקובץ שלך!
def generate_prediction(df, mapping):
    cards = []
    used_cards = set()

    for suit_name, suit_column in mapping.items():
        values = range(1, 14)
        freq_series = df[suit_column].apply(convert_card_value).value_counts().reindex(range(1, 14), fill_value=1).values
        super_bonus = calculate_super_trend_bonus(df, suit_column)

        trend_boost = np.random.uniform(0.8, 2.8, size=13)
        explosive_factor = np.random.uniform(1.0, 4.0, size=13)
        time_factor = np.random.uniform(0.9, 1.2, size=13)

        combined_weights = freq_series * 0.25 + trend_boost * 0.25 + explosive_factor * 0.2 + time_factor * 0.05 + super_bonus * 0.25

        chosen_card = weighted_random_choice(values, combined_weights, used_cards)
        used_cards.add(chosen_card)
        cards.append({"suit": suit_name, "card": chosen_card})

    return cards

# בחירת תוצאה חכמה

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

# Streamlit UI
st.set_page_config(page_title="מנוע חיזוי מותאם אישית", page_icon="🎴", layout="centered")
st.title("🎴 תחזית מותאמת אישית לצ׳אנס (לפי הקובץ הרשמי שלך)")

uploaded_file = st.file_uploader("📥 העלה את קובץ ה-CSV שלך מהאתר הרשמי:", type=["csv"])
df = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
        st.success("✅ הקובץ נטען בהצלחה!")
        df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']
        df = df[['תאריך', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']]
        mapping = {"לב שחור": "לב שחור", "לב אדום": "לב אדום", "יהלום": "יהלום", "תלתן": "תלתן"}

        st.markdown("### 50 הגרלות אחרונות:")
        display_df = df.head(50).copy()
        for suit in ["לב שחור", "לב אדום", "יהלום", "תלתן"]:
            display_df[suit] = display_df[suit].apply(convert_card_value).apply(
                lambda x: f"{x} {icons[suit]}" if pd.notnull(x) else x
            )
        st.dataframe(display_df)

    except Exception as e:
        st.error(f"❗ שגיאה בטעינת הקובץ: {e}")

if uploaded_file is not None and st.button("✨ צור תחזית חכמה"):
    options = [generate_prediction(df, mapping) for _ in range(6)]

    for idx, option in enumerate(options, 1):
        st.markdown(f"#### 🃏 תחזית לאפשרות {idx}")

        table_data = {f"{icons[item['suit']]} {item['suit']}": [
            "A" if item['card'] == 1 else "J" if item['card'] == 11 else "Q" if item['card'] == 12 else "K" if item['card'] == 13 else item['card']
            ] for item in option
        }
        table_df = pd.DataFrame(table_data)
        st.table(table_df)

st.markdown("---")
st.markdown("### 📖 איך זה עובד:")
st.markdown("""
- המערכת מזהה את סדר העמודות מהקובץ שלך
-מציגה 50 הגרלות אחרונות 
- מבצעת חיזוי סופר חכם על פי רצפים, מגמות, שיקופים וראשוניים.
- נבנה על ידי ליביו הוליביה
""")
