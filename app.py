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

def convert_card_value(value):
    try:
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
        elif isinstance(value, (int, float)):
            return int(value)
    except:
        return None
    return value

def display_card_value(val):
    if val == 1:
        return "A"
    elif val == 11:
        return "J"
    elif val == 12:
        return "Q"
    elif val == 13:
        return "K"
    return str(val)

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

def calculate_super_trend_bonus(df, suit_column):
    values = range(1, 14)
    column_values = df[suit_column].apply(convert_card_value).dropna().values[:50]
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

        for val in column_values[i:i+4]:
            if val > 1:
                bonus_weights[val - 2] += 0.8
            if val < 13:
                bonus_weights[val] += 0.8

        if i >= 7:
            back_val = column_values[i - 7]
            bonus_weights[back_val - 1] += 1.2

        if column_values[i] % 2 == 0 and column_values[i+1] % 2 == 0 and column_values[i+2] % 2 == 0:
            for prime in [2, 3, 5, 7, 11]:
                bonus_weights[prime - 1] += 1.5

        if diff1 > 0 and diff2 < 0:
            mid_val = (column_values[i] + column_values[i+2]) // 2
            bonus_weights[mid_val - 1] += 1.3

        for prime in [2, 3, 5, 7, 11]:
            bonus_weights[prime - 1] += 1.2

        if column_values[i] in [11, 12, 13]:
            for mid in range(5, 10):
                bonus_weights[mid - 1] += 1.5

        if i < len(column_values) - 4:
            diagonal_val = (column_values[i] + column_values[i+3]) // 2
            if 1 <= diagonal_val <= 13:
                bonus_weights[diagonal_val - 1] += 1.4

        if i >= 9:
            moving_avg = int(np.mean(column_values[i-9:i+1]))
            if 1 <= moving_avg <= 13:
                bonus_weights[moving_avg - 1] += 1.2

        if abs(diff1) == 1 and abs(diff2) == 2:
            next_val = column_values[i + 2] + 3
            if 1 <= next_val <= 13:
                bonus_weights[next_val - 1] += 1.3

        if column_values[i] in [2, 3, 5, 7, 11] and column_values[i+1] in [2, 3, 5, 7, 11]:
            for composite in [4, 6, 8, 9, 10, 12]:
                bonus_weights[composite - 1] += 1.4

        for mid_num in [7, 8, 9]:
            bonus_weights[mid_num - 1] += 1.3

    return bonus_weights

def generate_prediction(df):
    cards = []
    used_cards = set()

    for suit in suits:
        values = range(1, 14)
        freq_series = df[suit].apply(convert_card_value).value_counts().reindex(range(1, 14), fill_value=1).values
        super_bonus = calculate_super_trend_bonus(df, suit)

        trend_boost = np.random.uniform(0.8, 2.8, size=13)
        explosive_factor = np.random.uniform(1.0, 4.0, size=13)
        time_factor = np.random.uniform(0.9, 1.2, size=13)

        combined_weights = freq_series * 0.25 + trend_boost * 0.25 + explosive_factor * 0.2 + time_factor * 0.05 + super_bonus * 0.25

        chosen_card = weighted_random_choice(values, combined_weights, used_cards)
        used_cards.add(chosen_card)
        cards.append({"suit": suit, "card": chosen_card})

    return cards

st.set_page_config(page_title="חיזוי צ׳אנס חכם", layout="centered")
st.title("🎴 חיזוי הגרלה חכם לצ׳אנס")

uploaded_file = st.file_uploader("📥 העלה את קובץ היסטוריית ההגרלות (CSV):", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']
    df = df[['תאריך', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']]

    st.subheader("50 הגרלות אחרונות:")
    display_df = df.head(50).copy()
    for suit in suits:
        display_df[suit] = display_df[suit].apply(convert_card_value).apply(lambda x: f"{display_card_value(x)} {icons[suit]}" if pd.notnull(x) else x)
    st.dataframe(display_df)

    if st.button("✨ צור תחזית חכמה"):
        predictions = [generate_prediction(df) for _ in range(6)]

        for idx, pred in enumerate(predictions, start=1):
            st.markdown(f"#### תחזית מספר {idx}")
            row = " | ".join([f"{icons[item['suit']]} {display_card_value(item['card'])}" for item in pred])
            st.write(row)

st.markdown("---")
st.markdown("נבנה ע""י ליביו הוליביה")
