import streamlit as st
import pandas as pd
import numpy as np

ordered_suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {
    "לב שחור": "♠️", 
    "לב אדום": "♥️",
    "יהלום": "♦️",
    "תלתן": "♣️",
}

# קלפים מורשים בצ'אנס
allowed_cards = [1, 7, 8, 9, 10, 11, 12, 13]

# קשרי משיכה ישירים לפי המשחק
pull_relations_manual = {
    7: [8, 9, 10],
    8: [9, 11, 13],
    9: [8, 10, 11],
    10: [11, 12, 13],
    11: [10, 12, 13],
    12: [11, 13, 1],
    13: [10, 11, 1],
    1: [8, 10, 13]
}

# קשרי אלכסונים
diagonal_relations_manual = {
    7: [8, 9, 1],
    8: [9, 11, 7],
    9: [11, 7, 10],
    10: [11, 12, 13],
    11: [12, 13, 7],
    12: [13, 1, 9],
    13: [1, 8, 10],
    1: [9, 10, 12]
}

# דפוסים נוספים
same_card_other_suit = [7, 8, 9, 10, 11, 12, 13, 1]
triples_after_pairs = [7, 8, 9, 11, 13]
increment_decrement_cards = [7, 8, 9, 10, 11, 12, 13, 1]

def convert_card_value(value):
    if isinstance(value, str):
        value = value.strip()
        if value == 'A': return 1
        elif value == 'J': return 11
        elif value == 'Q': return 12
        elif value == 'K': return 13
        elif value.isdigit():
            return int(value)
    elif isinstance(value, (int, float)):
        return int(value)
    return None

def display_card_value(val):
    if val == 1: return "A"
    elif val == 11: return "J"
    elif val == 12: return "Q"
    elif val == 13: return "K"
    return str(val)

def build_chance_weights(df, suit):
    last_50 = df.sort_values(by='מספר הגרלה', ascending=False).head(50)
    freq_series = last_50[suit].value_counts().reindex(allowed_cards, fill_value=1).values
    trend = np.random.uniform(0.8, 2.0, size=len(allowed_cards))
    explosive = np.random.uniform(1.0, 3.0, size=len(allowed_cards))
    cycle_boost = np.random.uniform(1.05, 1.15, size=len(allowed_cards))

    pull_factor = np.ones(len(allowed_cards))
    diagonal_factor = np.ones(len(allowed_cards))
    extra_pattern_factor = np.ones(len(allowed_cards))

    for idx, i in enumerate(allowed_cards):
        if i in pull_relations_manual:
            for pulled in pull_relations_manual[i]:
                if pulled in allowed_cards:
                    pull_factor[allowed_cards.index(pulled)] += 2.0

        if i in diagonal_relations_manual:
            for diag in diagonal_relations_manual[i]:
                if diag in allowed_cards:
                    diagonal_factor[allowed_cards.index(diag)] += 1.8

        if i in same_card_other_suit:
            extra_pattern_factor[idx] += 1.3

        if i in triples_after_pairs:
            extra_pattern_factor[idx] += 1.2

        if i in increment_decrement_cards:
            extra_pattern_factor[idx] += 1.4

    combined = freq_series * 0.15 + trend * 0.1 + explosive * 0.1
    combined *= cycle_boost
    combined *= (pull_factor * 0.3)
    combined *= (diagonal_factor * 0.25)
    combined *= extra_pattern_factor * 0.15

    return combined / combined.sum()

def predict_chance(df):
    prediction = []
    for suit in ordered_suits:
        base_weights = build_chance_weights(df, suit)
        chosen_card = np.random.choice(allowed_cards, p=base_weights)
        prediction.append({"suit": suit, "card": chosen_card})
    return prediction

st.set_page_config(page_title="אלגוריתם מותאם לצ'אנס (7 עד אס)")
st.title("🎴 תחזיות סופיות לצ'אנס — עם כל הדפוסים מ-7 עד אס בלבד!")

uploaded_file = st.file_uploader("📥 העלה קובץ CSV עם היסטוריית הגרלות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ["תלתן", "יהלום", "לב אדום", "לב שחור"]:
        df[suit] = df[suit].apply(convert_card_value)

    st.write("### 50 ההגרלות האחרונות:")
    preview = df.sort_values(by='מספר הגרלה', ascending=False).head(50).copy()
    preview = preview[['תאריך', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']]
    for suit in ["לב שחור", "לב אדום", "יהלום", "תלתן"]:
        preview[suit] = preview[suit].apply(display_card_value)
    st.dataframe(preview)

    st.write("### 25 תחזיות עם כל הדפוסים (מ-7 עד אס):")
    table_html = "<table style='width:100%; border-collapse: collapse;'>"
    table_html += "<tr><th>#</th><th>♠️ עלה</th><th>♥️ לב</th><th>♦️ יהלום</th><th>♣️ תלתן</th></tr>"

    for i in range(1, 26):
        prediction = predict_chance(df)
        ordered_prediction = [next(p for p in prediction if p['suit'] == suit) for suit in ordered_suits]
        row = f"<tr><td style='text-align:center;'>{i}</td>"
        for p in ordered_prediction:
            row += f"<td style='text-align:center; padding:5px; border:1px solid #ddd;'>{icons[p['suit']]} {display_card_value(p['card'])}</td>"
        row += "</tr>"
        table_html += row

    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)

st.markdown("---")
st.markdown("פותח ע\"י ליביו הוליביה — האלגוריתם האמיתי לצ'אנס, מ-7 עד אס בלבד!")
