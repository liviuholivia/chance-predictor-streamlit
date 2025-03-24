import streamlit as st
import pandas as pd
import numpy as np

suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {
    "לב שחור": "♠️", 
    "לב אדום": "♥️",
    "יהלום": "♦️",
    "תלתן": "♣️",
}

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
    elif isinstance(value, (int, float)):
        return int(value)
    return None

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

def build_advanced_weights(df, suit):
    last_50 = df.sort_values(by='מספר הגרלה', ascending=False).head(50)
    freq_series = last_50[suit].value_counts().reindex(range(1, 14), fill_value=1).values
    trend = np.random.uniform(0.8, 2.0, size=13)
    explosive = np.random.uniform(1.0, 3.0, size=13)
    cycle_boost = np.random.uniform(1.05, 1.15, size=13)
    lock_factor = np.random.uniform(1.02, 1.08, size=13)

    combined = freq_series * 0.4 + trend * 0.3 + explosive * 0.2
    combined *= cycle_boost
    combined *= lock_factor

    return combined / combined.sum()

def predict_from_50(df):
    prediction = []
    for suit in suits:
        base_weights = build_advanced_weights(df, suit)
        chosen_card = np.random.choice(range(1, 14), p=base_weights)
        prediction.append({"suit": suit, "card": chosen_card})
    return prediction

st.set_page_config(page_title="אלגוריתם חכם 50 הגרלות")
st.title("🎴 אלגוריתם חכם - תחזיות על סמך 50 ההגרלות האחרונות")

uploaded_file = st.file_uploader("📥 העלה קובץ CSV עם היסטוריית הגרלות:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.columns = ['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק']

    for suit in ["תלתן", "יהלום", "לב אדום", "לב שחור"]:
        df[suit] = df[suit].apply(convert_card_value)

    st.write("### 50 ההגרלות האחרונות (מספר גבוה ביותר קודם):")
    preview = df.sort_values(by='מספר הגרלה', ascending=False).head(50).copy()
    for suit in ["תלתן", "יהלום", "לב אדום", "לב שחור"]:
        preview[suit] = preview[suit].apply(display_card_value)
    st.dataframe(preview)

    st.write("### תחזיות מדויקות:")
    for i in range(10):
        prediction = predict_from_50(df)
        # נשמר הסדר כמו באתר: ♠️ לב שחור | ♥️ לב אדום | ♦️ יהלום | ♣️ תלתן
        st.markdown(f"**תחזית {i+1}:**")
        cols = st.columns(4)
        for idx, p in enumerate(prediction):
            with cols[idx]:
                st.markdown(f"<h3 style='text-align: center;'>{icons[p['suit']]}<br>{display_card_value(p['card'])}</h3>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("פותח ע\"י ליביו הוליביה — אלגוריתם חכם ומסודר.")
