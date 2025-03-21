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

# האלגוריתם המורחב עם כל הדפוסים:
def calculate_super_trend_bonus(df, suit_column):
    values = range(1, 14)
    column_values = df[suit_column].apply(convert_card_value).values[:50]
    bonus_weights = np.ones(13)

    for i in range(len(column_values) - 3):
        diff1 = column_values[i + 1] - column_values[i]
        diff2 = column_values[i + 2] - column_values[i + 1]

        # רצפים עולים/יורדים
        if abs(diff1) == 1 and abs(diff2) == 1 and (diff1 == diff2):
            next_val = column_values[i + 2] + diff2
            if 1 <= next_val <= 13:
                bonus_weights[next_val - 1] += 2.0

        # מדרגות יורדות (מדרגה הפוכה)
        if diff1 < 0 and diff2 < 0:
            next_val = column_values[i + 2] + 3
            if next_val <= 13:
                bonus_weights[next_val - 1] += 2.5

        # חזרתיות תוך 3–5 הגרלות
        last_occurrences = df.iloc[i:i+5].applymap(convert_card_value).values.flatten()
        for val in values:
            if val in last_occurrences:
                bonus_weights[val - 1] += 1.4

        # שכנים של מספרים שהופיעו
        for val in column_values[i:i+4]:
            if val > 1:
                bonus_weights[val - 2] += 0.8
            if val < 13:
                bonus_weights[val] += 0.8

        # מחזוריות כל 7–9 הגרלות
        if i >= 7:
            back_val = column_values[i - 7]
            bonus_weights[back_val - 1] += 1.2

        # ראשוני אחרי רצף זוגי
        if column_values[i] % 2 == 0 and column_values[i+1] % 2 == 0 and column_values[i+2] % 2 == 0:
            for prime in [2, 3, 5, 7, 11]:
                bonus_weights[prime - 1] += 1.5

        # תבנית גלים
        if diff1 > 0 and diff2 < 0:
            mid_val = (column_values[i] + column_values[i+2]) // 2
            bonus_weights[mid_val - 1] += 1.3

        # בונוס לראשוניים כלליים
        for prime in [2, 3, 5, 7, 11]:
            bonus_weights[prime - 1] += 1.2

        # ריבאונד אחרי קלפים גבוהים
        if column_values[i] in [11, 12, 13]:
            for mid in range(5, 10):
                bonus_weights[mid - 1] += 1.5

        # אלכסון בין צורות (דפוס בין העמודות)
        if i < len(column_values) - 4:
            diagonal_val = (column_values[i] + column_values[i+3]) // 2
            if 1 <= diagonal_val <= 13:
                bonus_weights[diagonal_val - 1] += 1.4

        # ממוצע נע בטווח 10 הגרלות אחרונות
        if i >= 9:
            moving_avg = int(np.mean(column_values[i-9:i+1]))
            if 1 <= moving_avg <= 13:
                bonus_weights[moving_avg - 1] += 1.2

        # דפוס פיבונאצ'י חלקי (הפרשים של 1, 2, 3 החוזרים)
        if abs(diff1) == 1 and abs(diff2) == 2:
            next_val = column_values[i + 2] + 3
            if 1 <= next_val <= 13:
                bonus_weights[next_val - 1] += 1.3

        # מספר מרוכב אחרי רצף ראשוניים
        if column_values[i] in [2, 3, 5, 7, 11] and column_values[i+1] in [2, 3, 5, 7, 11]:
            for composite in [4, 6, 8, 9, 10, 12]:
                bonus_weights[composite - 1] += 1.4

        # בונוס קבוע למספרי אמצע (7, 8, 9)
        for mid_num in [7, 8, 9]:
            bonus_weights[mid_num - 1] += 1.3

    return bonus_weights
