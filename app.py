import streamlit as st
import pandas as pd
import random

# הגדרת המרות מספרים לקלפים
def card_name(num):
    if num == 1:
        return "A"
    elif num == 11:
        return "J"
    elif num == 12:
        return "Q"
    elif num == 13:
        return "K"
    else:
        return str(num)

suits = ["לב שחור", "לב אדום", "יהלום", "תלתן"]
icons = {
    "לב שחור": "♠️",
    "לב אדום": "♥️",
    "יהלום": "♦️",
    "תלתן": "♣️"
}

# קריאת קובץ
uploaded_file = st.file_uploader("📥 העלה קובץ CSV עם היסטוריית הגרלות:", type=["csv"])
df = None
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = df.head(50)  # מציג 50 הגרלות אחרונות
    df_display = df.copy()

    # המרה להצגת הקלפים בטבלה
    for suit in suits:
        df_display[suit] = df_display[suit].apply(card_name)

    st.write("### 50 התוצאות האחרונות:")
    st.dataframe(df_display)

# פונקציית תחזית פשוטה שמבוססת על משקלים אקראיים לדוגמה (מקום האלגוריתם החכם שלך)
def predict_next_card():
    return random.randint(7, 13)

def generate_prediction():
    prediction = {}
    for suit in suits:
        prediction[suit] = predict_next_card()
    return prediction

# תצוגת התחזיות
if st.button("✨ צור 25 תחזיות") and df is not None:
    st.write("## 25 תחזיות:")
    for i in range(1, 26):
        pred = generate_prediction()
        prediction_line = " | ".join([
            f"{icons[s]} {card_name(pred[s])}"
            for s in suits
        ])
        st.markdown(f"**תחזית {i}:** {prediction_line}")
