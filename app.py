import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
from bs4 import BeautifulSoup

# הגדרת הצורות והאייקונים
ordered_suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {"לב שחור": "♠️", "לב אדום": "♥️", "יהלום": "♦️", "תלתן": "♣️"}
allowed_cards = [7, 8, 9, 10, 11, 12, 13, 14]

def display_card_value(val):
    return {11: "J", 12: "Q", 13: "K", 14: "A"}.get(val, str(val))

def convert_card_value(value):
    if isinstance(value, str):
        if value.strip() == 'A': return 14
        elif value.strip() == 'J': return 11
        elif value.strip() == 'Q': return 12
        elif value.strip() == 'K': return 13
        elif value.isdigit(): return int(value)
    return value

# יחסי משיכות ואלכסונים
pull_relations = {
    7: [8, 9, 10, 11, 14], 8: [9, 11, 13, 14], 9: [10, 12, 13, 14],
    10: [7, 14, 11, 9], 11: [9, 13, 10, 8], 12: [11, 9, 14, 10],
    13: [14, 10, 8, 9], 14: [9, 12, 10, 7]
}

diagonal_relations = {
    7: [9, 10, 13, 14], 8: [10, 11, 12, 14], 9: [11, 13, 7, 14],
    10: [7, 9, 14, 12], 11: [9, 12, 7, 14], 12: [10, 13, 8, 14],
    13: [7, 10, 14, 9], 14: [9, 11, 12, 10]
}

def build_weights(df, suit):
    recent = df.sort_values('מספר הגרלה', ascending=False).head(50)
    freq = recent[suit].value_counts().reindex(allowed_cards, fill_value=1).values

    pull_factor = np.ones(len(allowed_cards))
    diagonal_factor = np.ones(len(allowed_cards))
    lock_factor = np.ones(len(allowed_cards))
    correction_factor = np.ones(len(allowed_cards))

    last_card = recent.iloc[0][suit]
    last_date = pd.to_datetime(recent.iloc[0]['תאריך'])
    weekday = last_date.weekday()

    for idx, card in enumerate(allowed_cards):
        if card in pull_relations:
            for pull_card in pull_relations[card]:
                if pull_card in allowed_cards:
                    pull_factor[allowed_cards.index(pull_card)] += 2.2

        if card in diagonal_relations:
            for diag in diagonal_relations[card]:
                if diag in allowed_cards:
                    diagonal_factor[allowed_cards.index(diag)] += 2

        if card == last_card:
            lock_factor[idx] += 2.7

        if abs(card - last_card) >= 4:
            correction_factor[idx] += 3.5

        if weekday in [0, 1] and suit in ["לב אדום", "יהלום"]:
            correction_factor[idx] += 1.4
        if weekday in [4, 5] and suit in ["תלתן", "לב שחור"]:
            pull_factor[idx] += 1.7

    base = freq * 0.18 + np.random.uniform(0.9, 1.1, size=len(allowed_cards))
    combined = base * pull_factor * 0.3 * diagonal_factor * 0.25 * lock_factor * 0.15 * correction_factor * 0.2

    return combined / combined.sum()

def predict_next(df):
    prediction = []
    for suit in ordered_suits:
        weights = build_weights(df, suit)
        chosen = np.random.choice(allowed_cards, p=weights)
        prediction.append({"suit": suit, "card": chosen})
    return prediction

def fetch_chance_data():
    url = "https://www.pais.co.il/chance/archive.aspx"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table', {'id': 'tblArchiveResults'})
    rows = table.find_all("tr")[1:]

    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 6:
            date = cols[0].text.strip()
            draw_num = int(cols[1].text.strip())
            clover, diamond, heart, spade = cols[2].text.strip(), cols[3].text.strip(), cols[4].text.strip(), cols[5].text.strip()
            data.append([date, draw_num, clover, diamond, heart, spade, ''])

    df = pd.DataFrame(data, columns=['תאריך', 'מספר הגרלה', 'תלתן', 'יהלום', 'לב אדום', 'לב שחור', 'ריק'])
    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df[suit] = df[suit].apply(convert_card_value)

    return df.sort_values(by='מספר הגרלה', ascending=False).head(50)

st.title("🎴 אלגוריתם סופר חכם + בוט למשיכת תוצאות")

if st.button("🔄 משוך תוצאות מהאתר"):
    df = fetch_chance_data()

    df_display = df.copy()
    for suit in ['תלתן', 'יהלום', 'לב אדום', 'לב שחור']:
        df_display[suit] = df_display[suit].apply(display_card_value)

    st.write("### טבלת 50 הגרלות אחרונות (בוט):")
    st.write(df_display[['תאריך', 'מספר הגרלה', 'לב שחור', 'לב אדום', 'יהלום', 'תלתן']])

    st.write("### 10 תחזיות:")
    predictions_data = []
    for i in range(1, 11):
        prediction = predict_next(df)
        row = {p['suit']: display_card_value(p['card']) for p in prediction}
        predictions_data.append(row)

    pred_df = pd.DataFrame(predictions_data)
    pred_df = pred_df[ordered_suits]
    pred_df.columns = [f"{icons[s]} {s}" for s in ordered_suits]

    st.table(pred_df)

st.markdown("פותח על ידי ליביו הוליביה — עם בוט משולב ואלגוריתם מלא!")
