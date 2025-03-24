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

# קשרי משיכה ישירים
pull_relations_manual = {
    8: [9, 11, 13],
    9: [8, 11, 10],
    10: [13, 11, 7],
    11: [10, 9, 7],
    13: [10, 12, 8]
}

# קשרי אלכסונים
diagonal_relations_manual = {
    9: [11, 7, 13],
    10: [10, 7, 11],
    7: [8, 13, 1],
    11: [12, 7, 13],
    8: [9, 11, 7],
    13: [10, 13, 1],
    12: [8, 10, 13]
}

# דפוסים נוספים
same_card_other_suit = [8, 9, 11, 13]
triples_after_pairs = [7, 8, 11]
increment_decrement_cards = [7, 8, 9, 10, 11]

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

def build_full_weights(df, suit):
    last_50 = df.sort_values(by='מספר הגרלה', ascending=False).head(50)
    freq_series = last_50[suit].value_counts().reindex(range(1, 14), fill_value=1).values
    trend = np.random.uniform(0.8, 2.0, size=13)
    explosive = np.random.uniform(1.0, 3.0, size=13)
    cycle_boost = np.random.uniform(1.05, 1.15, size=13)

    pull_factor = np.ones(13)
    diagonal_factor = np.ones(13)
    extra_pattern_factor = np.ones(13)

    for i in range(1, 14):
        if i in pull_relations_manual:
            for pulled in pull_relations_manual[i]:
                pull_factor[pulled - 1] += 2.0

        if i in diagonal_relations_manual:
            for diag in diagonal_relations_manual[i]:
                diagonal_factor[diag - 1] += 1.8

        if i in same_card_other_suit:
            extra_pattern_factor[i - 1] += 1.3

        if i in triples_after_pairs:
            extra_pattern_factor[i - 1] += 1.2

        if i in increment_decrement_cards:
            extra_pattern_factor[i - 1] += 1.4

    combined = freq_series * 0.15 + trend * 0.1 + explosive * 0.1
    combined *= cycle_boost
    combined *= (pull_factor * 0.3)
    combined *= (diagonal_factor * 0.25)
    combined *= extra_pattern_factor * 0.15

    return combined / combined.sum()

def predict_full_model(df):
    prediction = []
    for suit in ordered_suits:
        base_weights = build_full_weights(df, suit)
        chosen_card = np.random.choice(range(1, 14), p=base_weights)
        prediction.append({"suit": suit, "card": chosen_card})
    return prediction

st.set_page_config(page_title="אלגוריתם מלא - כל הדפוסים המשולבים")
st.title("🎴 תחזיות סופיות - כל הדפוסים, כל האלכסונים, וכל המשיכות!")

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

    st.write("### 25 תחזיות עם כל הדפוסים:")
    table_html = "<table style='width:100%; border-collapse: collapse;'>"
    table_html += "<tr><th>#</th><th>♠️ עלה</th><th>♥️ לב</th><th>♦️ יהלום</th><th>♣️ תלתן</th></tr>"

    for i in range(1, 26):
        prediction = predict_full_model(df)
        ordered_prediction = [next(p for p in prediction if p['suit'] == suit) for suit in ordered_suits]
        row = f"<tr><td style='text-align:center;'>{i}</td>"
        for p in ordered_prediction:
            row += f"<td style='text-align:center; padding:5px; border:1px solid #ddd;'>{icons[p['suit']]} {display_card_value(p['card'])}</td>"
        row += "</tr>"
        table_html += row

    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)

st.markdown("---")
st.markdown("פותח ע\"י ליביו הוליביה — האלגוריתם הסופי המשלב הכל!")
